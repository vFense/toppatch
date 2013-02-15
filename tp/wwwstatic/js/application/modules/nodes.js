define(
    ['jquery', 'underscore', 'backbone', 'modules/lists/pageable'],
    function ($, _, Backbone, Pager) {
        "use strict";
        var exports = {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/nodes.json',
                _defaultParams: {
                    count: 20,
                    offset: 0,
                    filterby: '',
                    by_os: ''
                }
            }),
            TagCollection: Backbone.Collection.extend({
                baseUrl: '/api/tagging/listByTag.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Pager.View.extend({
                initialize: function (options) {
                    Pager.View.prototype.initialize.call(this, options);
                    this.tagcollection = new exports.TagCollection();
                    this.listenTo(this.tagcollection, 'reset', this.onRender);
                    this.tagcollection.fetch();
                },
                /*events: {
                    'change select[name=filter]': 'filterByTag'
                },*/
                filterByTag: function (event) {
                    var filterBy = $(event.currentTarget).val(),
                        view = event.data;
                    view.collection.params.filterby = filterBy === 'none' ? '' : filterBy;
                    view.collection.params.by_os = '';
                    view.collection.fetch();
                },
                onRender: function () {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        tags            = this.tagcollection.toJSON(),
                        $el             = this.$el,
                        $header         = $el.find('header'),
                        $legend         = newElement('div').addClass('legend'),
                        $host           = newElement('strong').html('Host Name'),
                        $statusSpan     = newElement('span').html('Status — ').append($host, ' — Host OS'),
                        $done           = newElement('span').addClass('done').html('Done'),
                        $pend           = newElement('span').addClass('pend').html('Pending'),
                        $need           = newElement('span').addClass('need').html('Available'),
                        $fail           = newElement('span').addClass('fail').html('Failed'),
                        $spanRight      = newElement('span').addClass('patches inlineBlock pull-right')
                                            .html('Patches ').append($done, ' / ', $pend, ' / ', $need, ' / ', $fail),
                        $nullOption     = newElement('option').attr('value', 'none').html('None'),
                        $select         = newElement('select').addClass('btn btn-mini').attr('name', 'filter').append($nullOption);
                    $el.find('.legend').remove();
                    $legend.append($statusSpan, $spanRight);
                    $header.after($legend);
                    if (tags.length) {
                        _.each(tags, function (tag) {
                            var $option = newElement('option').html(tag.tag_name);
                            $select.append($option);
                        });
                        $header.find('.pull-right').prepend($select);
                        $select.change(this, this.filterByTag);
                    }
                },
                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        id          = item.get('id'),
                        osIcon      = this.printOsIcon(item.get('os/name')),
                        displayName = this.displayName(item),
                        status      = this.getStatus(item),
                        $done       = newElement('span').addClass('done').html(item.get('patch/done')),
                        $pend       = newElement('span').addClass('pend').html(item.get('patch/pend')),
                        $need       = newElement('span').addClass('need').html(item.get('patch/need')),
                        $fail       = newElement('span').addClass('fail').html(item.get('patch/fail')),
                        $iconCaret  = newElement('i').addClass('icon-caret-right'),
                        $iconStatus = newElement('i').addClass(status.className).css('color', status.color),
                        $iconOS     = newElement('i').addClass(osIcon),
                        $nameSpan   = newElement('strong').html(displayName),
                        $leftSpan   = newElement('span').addClass('desc span8')
                                        .append($iconStatus, ' — ', $iconOS, ' ', $nameSpan, ' — ', item.get('os/name')),
                        $rightSpan  = newElement('span').addClass('alignRight span4')
                                        .append($done, ' / ', $pend, ' / ', $need, ' / ', $fail, ' ', $iconCaret),
                        $href       = newElement('a').attr('href', '#nodes/' + id)
                                        .append($leftSpan, $rightSpan),
                        $container  = newElement('div').addClass('row-fluid').append($href),
                        $item       = newElement('div').addClass('item linked clearfix').append($container);
                    return $item;
                },
                displayName: function (item) {
                    return item.get('node_vm_name') ||
                        item.get('displayname') ||
                        item.get('computer/name') ||
                        item.get('hostname') ||
                        item.get('ip');
                },
                getStatus: function (item) {
                    var reboot      = item.get('reboot'),
                        hostStatus  = item.get('host/status'),
                        agentStatus = item.get('agent/status'),
                        icon = {};
                    if (reboot) {
                        icon.className = 'icon-warning-sign';
                        icon.color = 'orange';
                    } else if (hostStatus && agentStatus) {
                        icon.className = 'icon-ok';
                        icon.color = 'green';
                    } else {
                        icon.className = 'icon-warning-sign';
                        icon.color = 'red';
                    }
                    return icon;
                },
                printOsIcon: function (osname) {
                    var osClass = '';
                    if (osname.indexOf('CentOS') !== -1) {
                        osClass = 'icon-lin-centos';
                    } else if (osname.indexOf('Ubuntu') !== -1) {
                        osClass = 'icon-lin-ubuntu';
                    } else if (osname.indexOf('Fedora') !== -1) {
                        osClass = 'icon-lin-fedora';
                    } else if (osname.indexOf('Debian') !== -1) {
                        osClass = 'icon-lin-debian';
                    } else if (osname.indexOf('Red Hat') !== -1) {
                        osClass = 'icon-lin-redhat';
                    } else if (osname.indexOf('OS X') !== -1) {
                        osClass = 'icon-os-apple';
                    } else if (osname.indexOf('Linux') !== -1) {
                        osClass = 'icon-os-linux_1_';
                    } else if (osname.indexOf('Windows') !== -1) {
                        osClass = 'icon-os-win-03';
                    } else {
                        osClass = 'icon-laptop';
                    }
                    return osClass;
                }
            })
        };
        return exports;
    }
);

