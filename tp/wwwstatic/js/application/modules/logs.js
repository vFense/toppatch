define(
    ['jquery', 'underscore', 'backbone', 'app', 'modules/lists/pageable', 'text!templates/list.html'],
    function ($, _, Backbone, app, Pager, myTemplate) {
        "use strict";
        return {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/transactions/getTransactions'
            }),
            View: Pager.View.extend({
                renderModel: function (item) {
                    var newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        result = item.get('result'),

                        $item       = newElement('div').addClass('item'),
                        $div        = newElement('div').addClass('row-fluid'),
                        $operation  = newElement('small').addClass('span2'),
                        $desc       = newElement('small').addClass('desc span3'),
                        $error      = newElement('small').addClass('span5').html('&nbsp;'),
                        $date       = newElement('small').addClass('span2 alignRight');

                    $operation.append(item.get('operation').toUpperCase());
                    $desc.html(item.get('node_id'));
                    $date.html(item.get('operation_sent'));

                    if (_.isBoolean(result) && !result) {
                        $div.addClass('fail');
                        $error.append(
                            newElement('a')
                                .attr('rel', 'tooltip')
                                .attr('data-placement', 'right')
                                .attr('data-original-title', item.get('error'))
                                .html('Message').tooltip()
                        );
                    }

                    return $item.append(
                        $div.append($operation, $desc, $error, $date)
                    );
                }
            })
        };
    }
);
