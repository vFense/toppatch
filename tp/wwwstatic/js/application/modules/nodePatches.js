/**
 * Created with PyCharm.
 * User: parallels
 * Date: 1/9/13
 * Time: 3:48 PM
 * To change this template use File | Settings | File Templates.
 */
define(
    ['jquery', 'underscore', 'backbone', 'text!templates/nodePatches.html'],
    function ($, _, Backbone, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();
                },
                events: {
                    'change select[name=severity]': 'filterBySeverity',
                    'click .toggle-all': 'toggleAll',
                    'click a.accordion-toggle': 'openAccordion',
                    'submit form': 'submit'
                },
                toggleAll: function (event) {
                    var status = event.target.checked,
                        form = $(event.target).parents('form');
                    $(form).find(":checkbox[name=patches]").each(function () {
                        $(this).attr("checked", status);
                    });
                },
                openAccordion: function (event) {
                    event.preventDefault();
                    if ($(event.target).attr('name') !== 'severity') {
                        var $href = $(event.currentTarget),
                            $icon = $href.find('i'),
                            $parent = $href.parents('.accordion-group'),
                            $body = $parent.find('.accordion-body'),
                            $popover = $body.find('input[name=schedule]');
                        if ($icon.hasClass('icon-circle-arrow-down')) {
                            $icon.attr('class', 'icon-circle-arrow-up');
                            $body.collapse('show');
                            setTimeout(function () {
                                $body.css('overflow', 'visible');
                            }, 300);
                        } else {
                            if ($popover.data('popover')) {
                                $popover.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                $popover.popover('hide');
                                $popover.attr('checked', false);
                            }
                            $icon.attr('class', 'icon-circle-arrow-down');
                            $body.collapse('hide');
                            $body.css('overflow', 'hidden');
                        }
                    }
                },
                filterBySeverity: function (event) {
                    var patchName, severity, patchId, $itemDiv, $div, $descSpan, $label, $input, $rightSpan, $href,
                        option = $(event.currentTarget).val(),
                        $accordion = $(event.currentTarget).parents('.accordion-group'),
                        $badge = $(event.currentTarget).siblings('span'),
                        $items = $accordion.find('.items'),
                        patchNeed = this.collection.toJSON()[0]['patch/need'],
                        newElement = function (element) {
                            return $(document.createElement(element));
                        },
                        i = 0,
                        counter = 0;
                    $items.empty();
                    for (i = 0; i < patchNeed.length; i += 1) {
                        if (option === patchNeed[i].severity) {
                            patchName = patchNeed[i].name;
                            severity = patchNeed[i].severity;
                            patchId = patchNeed[i].id;
                            $itemDiv = newElement('div').addClass('item clearfix').attr('title', patchName);
                            $div = newElement('div').addClass('row-fluid');
                            $descSpan = newElement('span').addClass('desc span8');
                            $label = newElement('label').addClass('checkbox inline').html(patchName);
                            $input = newElement('input').attr({type: 'checkbox', name: 'patches', value: patchId, id: patchId});
                            $rightSpan = newElement('span').addClass('span4 alignRight');
                            $href = newElement('a').attr('href', '#patches/' + patchId).html('More information');
                            $rightSpan.append($href);
                            $descSpan.append($label.prepend($input));
                            $itemDiv.append($div.append($descSpan, $rightSpan));
                            $items.append($itemDiv);
                            counter += 1;
                        } else if (option === 'None') {
                            patchName = patchNeed[i].name;
                            severity = patchNeed[i].severity;
                            patchId = patchNeed[i].id;
                            $itemDiv = newElement('div').addClass('item clearfix').attr('title', patchName);
                            $div = newElement('div').addClass('row-fluid');
                            $descSpan = newElement('span').addClass('desc span8');
                            $label = newElement('label').addClass('checkbox inline').html(patchName);
                            $input = newElement('input').attr({type: 'checkbox', name: 'patches', value: patchId, id: patchId});
                            $rightSpan = newElement('span').addClass('span4 alignRight');
                            $href = newElement('a').attr('href', '#patches/' + patchId).html('More information');
                            $rightSpan.append($href);
                            $descSpan.append($label.prepend($input));
                            $itemDiv.append($div.append($descSpan, $rightSpan));
                            $items.append($itemDiv);
                            counter += 1;
                        }
                    }
                    if (counter === 0) {
                        $itemDiv = newElement('div').addClass('item clearfix');
                        $div = newElement('div').addClass('row-fluid');
                        $descSpan = newElement('span').addClass('desc span8').html('<em>No patches to display</em>');
                        $itemDiv.append($div.append($descSpan));
                        $items.append($itemDiv);
                    }
                    $badge.html(counter);
                },
                submit: function (evt) {
                    var item, span, label, checkbox, $scheduleForm, type, patches, url, offset, fields,
                        $form = $(evt.target),
                        schedule = $form.find('input[name="schedule"]:checked'),
                        time = '',
                        that = this;
                    if ($form.attr('id') !== 'reboot-form') {
                        fields = $form.find('input[name="patches"]:checked');
                        if (!fields.length) {
                            //alert('Please select at least one patch');
                            that.$el.find('.alert').removeClass('alert-success').addClass('alert-error').show().find('span').html('Please select at least one patch');
                            return false;
                        }
                    }
                    if (schedule.length !== 0) {
                        $scheduleForm = schedule.data('popover').options.content;
                        time = $scheduleForm.find('input[name=datepicker]').val() + ' ' + $scheduleForm.find('select[name=hours]').val() + ':' + $scheduleForm.find('select[name=minutes]').val() + ' ' + $scheduleForm.find('select[name=ampm]').val();
                        label = $scheduleForm.find('input[name=label]').val() || 'Default';
                        offset = $scheduleForm.find('select[name=offset]').val();
                    }
                    type = $form.attr('id');
                    patches = $form.find('input[name="patches"]:checked');
                    url = '/submitForm?' + $form.serialize();
                    url += time ? '&time=' + time + '&label=' + label + '&offset=' + offset : '';

                    $.post(url,
                        function (json) {
                            window.console.log(json);
                            //json.pass = false;
                            //json.message = 'Operation failed to send';
                            if (schedule.data('popover')) {
                                schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                schedule.popover('hide');
                                schedule.attr('checked', false);
                            }
                            if (json.pass) {
                                that.$el.find('.alert').removeClass('alert-error').addClass('alert-success').show().find('span').html('Operation sent.');
                                patches.each(function () {
                                    item = $(this).parents('.item');
                                    span = $(this).parents('span');
                                    label = $(this).parent();
                                    checkbox = $(this);

                                    checkbox.remove();
                                    var patch = label.html();
                                    span.html(patch);
                                    label.remove();
                                    if (type === 'available' || type === 'failed') {
                                        item.appendTo($('#pending').children());
                                        if ($('#no-pending')) {
                                            $('#no-pending').remove();
                                        }
                                    } else {
                                        item.remove();
                                    }
                                });
                                if ($form.find('input:checked').attr('checked')) {
                                    $form.find('input:checked').attr('checked', false);
                                }
                            } else {
                                that.$el.find('.alert').removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                    return false;
                },
                beforeRender: $.noop,
                onRender: function () {
                    var close;
                    this.$el.find('input[name=schedule]').each(function () {
                        $(this).popover({
                            placement: 'top',
                            title: 'Patch Scheduling<button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            content: $('#schedule-form').clone(),
                            trigger: 'click'
                        });
                    }).click(function () {
                        var popover = this;
                        if (popover.checked) {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            close = $(this).data('popover').$tip.find('button[name=close]');
                            close.unbind();
                            close.bind('click', function (event) {
                                event.preventDefault();
                                $(popover).data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                                $(popover).popover('hide');
                                popover.checked = false;
                            });
                        } else {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                        }
                    });
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var template = _.template(this.template),
                        data = this.collection.toJSON()[0];

                    this.$el.empty();

                    this.$el.html(template({model: data}));

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                }
            })
        };
        return exports;
    }
);