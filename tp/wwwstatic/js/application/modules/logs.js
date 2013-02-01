define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/lists/pageable'],
    function ($, _, Backbone, app, Pager) {
        "use strict";
        return {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/transactions/getTransactions'
            }),
            View: Pager.View.extend({
                onRender: function () {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        $legend = newElement('div').addClass('legend row-fluid'),
                        $operationSpan = newElement('strong').addClass('span2').html('Operation'),
                        $nodeSpan = newElement('strong').addClass('span2').html('Node'),
                        $ipSpan = newElement('strong').addClass('span2').html('IP'),
                        $userSpan = newElement('strong').addClass('span2').html('User'),
                        $errorSpan = newElement('strong').addClass('span2').html('Error'),
                        $spanRight = newElement('strong').addClass('span2 inlineBlock alignRight').html('Date');
                    $legend.append($operationSpan, $nodeSpan, $ipSpan, $userSpan, $errorSpan, $spanRight);
                    this.$el.find('header').after($legend);
                },
                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        result = item.get('result'),

                        $item       = newElement('div').addClass('item row-fluid'),
                        $operation  = newElement('div').addClass('span2'),
                        $node       = newElement('div').addClass('span2'),
                        $ip         = newElement('div').addClass('span2'),
                        $user       = newElement('div').addClass('span2'),
                        $error      = newElement('div').addClass('span2').html('&nbsp;'),
                        $date       = newElement('div').addClass('span2 alignRight');

                    $operation.append(item.get('operation').toUpperCase());
                    $node.html(this.displayName(item));
                    $user.html(item.get('username'));
                    $ip.html(item.get('node_ip_address'));
                    $date.html(item.get('operation_sent'));

                    if (_.isBoolean(result) && !result) {
                        $item.addClass('fail');
                        $error.append(
                            newElement('a')
                                .attr('rel', 'tooltip')
                                .attr('data-placement', 'right')
                                .attr('data-original-title', item.get('error'))
                                .html('Message').tooltip()
                        );
                    }

                    return $item.append($operation, $node, $ip, $user, $error, $date);
                },
                displayName: function (item) {
                    return item.get('node_vm_name') ||
                        item.get('node_display_name') ||
                        item.get('node_computer_name') ||
                        item.get('node_host_name');
                }
            })
        };
    }
);
