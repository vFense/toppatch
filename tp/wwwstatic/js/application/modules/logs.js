define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/lists/pageable'],
    function ($, _, Backbone, app, Pager) {
        "use strict";
        return {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/transactions/getTransactions'
            }),
            View: Pager.View.extend({
                beforeUpdateList: function () {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        $legend = newElement('div').addClass('legend row-fluid'),
                        $operationSpan = newElement('strong').addClass('span2').html('Operation'),
                        $nodeSpan = newElement('strong').addClass('span3').html('Node'),
                        $userSpan = newElement('strong').addClass('span2').html('User'),
                        $errorSpan = newElement('strong').addClass('span3'),
                        $spanRight = newElement('strong').addClass('span2 inlineBlock alignRight').html('Date');
                    $legend.append($operationSpan, $nodeSpan, $userSpan, $errorSpan, $spanRight);
                    this.$el.find('header').after($legend);
                },
                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        result = item.get('result'),

                        $item       = newElement('div').addClass('item row-fluid'),
                        $operation  = newElement('div').addClass('span2'),
                        $node       = newElement('div').addClass('span3'),
                        $user       = newElement('div').addClass('span2'),
                        $error      = newElement('div').addClass('span3').html('&nbsp;'),
                        $date       = newElement('div').addClass('span2 alignRight');

                    $operation.append(item.get('operation').toUpperCase());
                    $node.html(item.get('node_id'));
                    $user.html(item.get('username'));
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

                    this.$el.find('.legend').first().hide();

                    return $item.append($operation, $node, $user, $error, $date);
                }
            })
        };
    }
);
