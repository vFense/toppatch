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
                        $row        = newElement('div').addClass('row-fluid'),
                        $operation  = newElement('div').addClass('span2'),
                        $node       = newElement('div').addClass('span4'),
                        $error      = newElement('div').addClass('span4').html('&nbsp;'),
                        $date       = newElement('div').addClass('span2 alignRight');

                    $operation.append(item.get('operation').toUpperCase());
                    $node.html(item.get('node_id'));
                    $date.html(item.get('operation_sent'));

                    if (_.isBoolean(result) && !result) {
                        $row.addClass('fail');
                        $error.append(
                            newElement('a')
                                .attr('rel', 'tooltip')
                                .attr('data-placement', 'right')
                                .attr('data-original-title', item.get('error'))
                                .html('Message').tooltip()
                        );
                    }

                    return $item.append(
                        $row.append($operation, $node, $error, $date)
                    );
                }
            })
        };
    }
);
