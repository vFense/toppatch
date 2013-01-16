/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/11/13
 * Time: 7:16 AM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/lists/pageable'],
    function ($, _, Backbone, app, Pager) {
        "use strict";
        return {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/tagging/tagStats'
            }),
            View: Pager.View.extend({
                renderModel: function (item) {
                    var $icon,
                        newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        tagName = item.get('tag_name'),
                        tagId = item.get('tag_id'),
                        available = item.get('patches_available'),
                        completed = item.get('patches_completed'),
                        pending = item.get('patches_pending'),
                        failed = item.get('patches_failed'),
                        reboot = item.get('reboots_pending'),
                        agents_down = item.get('agents_down'),

                        $item       = newElement('div').addClass('item row-fluid'),
                        $link       = newElement('a').attr('href', '#tags/' + tagId),
                        $tag        = newElement('div').addClass('span2'),
                        $node       = newElement('div').addClass('span4'),
                        $error      = newElement('div').addClass('span4').html('&nbsp;'),
                        $stats      = newElement('div').addClass('span2 alignRight'),
                        $need       = newElement('span').addClass('need').html(available),
                        $pend       = newElement('span').addClass('pend').html(pending),
                        $fail       = newElement('span').addClass('fail').html(failed),
                        $done       = newElement('span').addClass('done').html(completed);

                    if (reboot) {
                        $icon = newElement('i').addClass('icon-warning-sign').css('color', 'orange');
                    } else if (!agents_down) {
                        $icon = newElement('i').addClass('icon-ok').css('color', 'green');
                    } else {
                        $icon = newElement('i').addClass('icon-warning-sign').css('color', 'red');
                    }

                    $tag.append($icon, ' - ', tagName);
                    $stats.append($done, ' / ', $pend, ' / ', $need, ' / ', $fail);
                    $link.append($tag, $node, $error, $stats);

                    return $item.append($link);
                }
            })
        };
    }
);
