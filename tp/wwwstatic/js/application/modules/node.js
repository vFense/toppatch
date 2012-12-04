define(
    ['jquery', 'underscore', 'backbone', 'app', 'text!templates/node.html', 'jquery.ui.datepicker' ],
    function ($, _, Backbone, app, myTemplate) {
        "use strict";
        var exports = {
            Collection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
                }
            }),
            TagCollection: Backbone.Collection.extend({
                baseUrl: 'api/tagging/listByTag.json',
                url: function () {
                    return this.baseUrl;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    _.bindAll(this, 'createtag');
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.tagcollection = new exports.TagCollection();
                    this.tagcollection.bind('reset', this.render, this);
                    this.tagcollection.fetch();

                },
                events: {
                    'click .disabled': function (e) { e.preventDefault(); },
                    'click #addTag': 'showtags',
                    'click #createtag': 'createtag',
                    'click button[name=dependencies]': 'showDependencies',
                    'click input[name=taglist]': 'toggletag',
                    'click #editDisplay': 'showEditDisplay',
                    'click a.accordion-toggle': 'openAccordion',
                    'submit form': 'submit'
                },
                beforeRender: $.noop,
                onRender: function () {
                    var close;
                    this.$el.find('#addTag').popover({
                        title: 'Tags Available<button type="button" class="btn btn-link pull-right" id="close"><i class="icon-remove"></i></button>',
                        html: true,
                        trigger: 'click',
                        content: $('#list-form')
                    });
                    this.$el.find('#editDisplay').popover({
                        title: '',
                        html: true,
                        trigger: 'click',
                        content: $('#display-name')
                    });
                    this.$el.find('input[name=schedule]').each(function () {
                        $(this).popover({
                            placement: 'top',
                            title: 'Patch Scheduling<button type="button" class="btn btn-link pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            content: $('#schedule-form').clone(),
                            trigger: 'click'
                        });
                    }).click(function () {
                        var popover = this;
                        if (popover.checked) {
                            $(this).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            close = $(this).data('popover').$tip.find('button[name=close]');
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
                        data = this.collection.toJSON()[0],
                        tagData = this.tagcollection.toJSON();

                    this.$el.html('');

                    this.$el.append(template({model: data, tags: tagData}));

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                submit: function (evt) {
                    var item, span, label, checkbox, $scheduleForm, type, patches, url, offset,
                        $form = $(evt.target),
                        schedule = $form.find('input[name="schedule"]:checked'),
                        time = '';
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
                                $('.alert').removeClass('alert-error').addClass('alert-success').show().find('span').html('Operation sent.');
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
                                $('.alert').removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                    return false;
                },
                showDependencies: function (event) {
                    event.preventDefault();
                    var list, node_id, patch_id, params,
                        popoverlink = $(event.currentTarget);

                    if (!popoverlink.data('popover')) {
                        popoverlink.popover({
                            title: 'Dependencies',
                            placement: 'right',
                            html: true,
                            content: $('#dependency-list').clone(),
                            trigger: 'click'
                        });
                        popoverlink.popover('show');
                        list = popoverlink.data('popover').tip().find('.items');
                        node_id = $('#reboot-form').find('input[name=node]').val();
                        patch_id = popoverlink.attr('value');
                        params = {
                            patch_id: patch_id,
                            node_id: node_id
                        };
                        window.console.log(params);
                        /*
                        $.post("/api/package/getDependencies", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    list.find('div[name=loading]').remove();
                                    list.append('<div class="item clearfix"><span>JSON CONTENT</span></div>');
                                }
                            });
                        */
                    }
                },
                showEditDisplay: function (event) {
                    var popover = $(event.currentTarget).data('popover'),
                        button = popover.$tip.find('button');
                    button.on('click', {view: this, popover: popover}, this.submitDisplayName);
                    return false;
                },
                submitDisplayName: function (event) {
                    var $em, $span,
                        $displayName = $(event.currentTarget).siblings('input'),
                        node_id = event.data.view.collection.id,
                        popover = event.data.popover,
                        $displayNameDiv = $('#editDisplay').parent();
                    if ($displayName.val()) {
                        $.post('api/node/modifyDisplayName', { nodeid: node_id, displayname: $displayName.val() }, function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                $em = $displayNameDiv.find('em');
                                $span = $displayNameDiv.find('span');
                                if ($em) { $em.remove(); }
                                if ($span) { $span.html($displayName.val()); }
                                popover.hide();
                            }
                        });
                    }
                },
                showtags: function (evt) {
                    var showInput, addTag, tagList, close,
                        popover = $(evt.target).parent().data('popover');
                    if (popover) {
                        showInput = popover.$tip.find('button');
                        close = popover.$tip.find('#close');
                        addTag = showInput.siblings('div').children('button');
                        tagList = popover.$tip.find('input[name=taglist]');
                        close.bind('click', function () { $(evt.target).parent().popover('hide'); });
                        tagList.bind('click', this.toggletag);
                        addTag.bind('click', this.createtag);
                        showInput.show().siblings('div').hide();
                        showInput.bind('click', function () {
                            $(this).hide().siblings('div').show();
                        });
                    }
                    return false;
                },
                createtag: function (evt) {
                    var params, tag, user, nodes, operation, list, checkboxlist, itemstring, tagname, notag,
                        that = this;
                    list = $('#taglist');
                    checkboxlist = $('#list-form').children('.list').children('.items');
                    operation = 'add_to_tag';
                    user = window.User.get('name');
                    tag = $(evt.currentTarget).siblings().val();
                    nodes = $(evt.currentTarget).parents('form').find('input[name=nodeid]').val();
                    params = {
                        nodes: [nodes],
                        user: user,
                        tag: tag,
                        operation: operation
                    };
                    $.post("/api/tagging/addTagPerNode", { operation: JSON.stringify(params) },
                        function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                notag = $('#notag');
                                if (notag) { notag.remove(); }
                                list.prepend('<span class="label label-info">' + tag + '</span>&nbsp;');
                                tagname = tag;
                                tag = 'value="' + tag + '"';
                                itemstring = '<div class="item clearfix">' +
                                                '<label class="checkbox">' + tagname +
                                                    '<input name="taglist" type="checkbox" checked="checked" ' + tag + '/>' +
                                                '</label>' +
                                            '</div>';
                                checkboxlist.append(itemstring);
                                checkboxlist.find('input[name=taglist]').on('click', that.toggletag);
                            }
                        });
                    return false;
                },
                toggletag: function (evt) {
                    var params, nodes, tag, user, list, notag,
                        checked = evt.currentTarget.checked;
                    list = $('#taglist');
                    user = window.User.get('name');
                    tag = $(evt.currentTarget).val();
                    nodes = $(evt.currentTarget).parents('form').find('input[name=nodeid]').val();
                    params = {
                        nodes: [nodes],
                        user: user,
                        tag: tag
                    };
                    if (checked) {
                        //add node to tag
                        notag = $('#notag');
                        if (notag) { notag.remove(); }
                        params.operation = 'add_to_tag';
                        $.post("/api/tagging/addTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    list.prepend('<span style="margin-right: 6px" class="label label-info" id="' + tag.replace(' ', '') + '">' + tag + '</span>');
                                }
                            });
                    } else {
                        //remove node from tag
                        params.operation = 'remove_from_tag';
                        $.post("/api/tagging/removeTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    $('#' + tag.replace(' ', '')).remove();
                                }
                            });
                    }
                },
                openAccordion: function (event) {
                    event.preventDefault();
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
                },
                beforeClose: function () {
                    var schedule = this.$el.find('input[name="schedule"]:checked'),
                        popover = this.$el.find('#addTag'),
                        dependency = this.$el.find('a[name=dependencies]'),
                        displayPopover = this.$el.find('#editDisplay');
                    if (displayPopover.data('popover')) { displayPopover.popover('destroy'); }
                    if (dependency.data('popover')) { dependency.popover('destroy'); }
                    if (popover.data('popover')) { popover.popover('destroy'); }
                    if (schedule.data('popover')) {
                        schedule.data('popover').options.content.find('input[name=datepicker]').datepicker('destroy');
                        schedule.popover('destroy');
                    }
                },
                clearFilter: function () {
                    this.collection.filter = '';
                }
            })
        };
        return exports;
    }
);
