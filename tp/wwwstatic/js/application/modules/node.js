define(
    ['jquery', 'underscore', 'backbone', 'd3', 'app', 'modules/tabNavigation', 'modules/nodePatches', 'modules/nodeVMware', 'text!templates/node.html', 'jquery.ui.datepicker' ],
    function ($, _, Backbone, d3, app, tabNav, patchesView, vmView, myTemplate) {
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
            VmCollection: Backbone.Collection.extend({
                baseUrl: 'api/virtual/node/info',
                url: function () {
                    return this.baseUrl + '?node_id=' + this.id;
                }
            }),
            TagsInNodeCollection: Backbone.Collection.extend({
                baseUrl: 'api/nodes.json',
                url: function () {
                    return this.baseUrl + '?id=' + this.id;
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    _.bindAll(this, 'createTag');
                    this.template = myTemplate;

                    this.tagsinnodecollection = new exports.TagsInNodeCollection();
                    this.tagsinnodecollection.bind('reset', this.updateTagList, this);

                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.id = this.collection.id;
                    this._rendered = false;
                    this._currentTab = '#nodes/' + this.id + '/patches';

                    this.tagcollection = new exports.TagCollection();
                    this.tagcollection.bind('reset', this.render, this);
                    this.tagcollection.fetch();

                    this.vmcollection = new exports.VmCollection();
                    this.vmcollection.bind('reset', this.render, this);
                    this.vmcollection.fetch();
                },
                events: {
                    'click .disabled': function (e) { e.preventDefault(); },
                    'click li a': 'changeView',
                    'click button[name=toggleAddTag]': 'showTags',
                    'click button[name=removeTag]': 'removeTag',
                    'click #createtag': 'createTag',
                    'click button[name=dependencies]': 'showDependencies',
                    'click input[name=taglist]': 'toggleTag',
                    'click #editDisplay': 'showEditOperation',
                    'click #editHost': 'showEditOperation',
                    'click button[name=showNetworking]': 'showNetworking',
                    'click button[name=agentOperation]': 'agentOperation',
                    'click button[name=nodeOperation]': 'nodeOperation',
                    'submit form': 'submit'
                },
                beforeRender: $.noop,
                onRender: function () {
                    var close, that = this;
                    this.stackedAreaGraph();
                    this.$el.find('i').each(function () {
                        $(this).tooltip();
                    });
                    this.$el.find('button[name=toggleAddTag]').popover({
                        placement: 'right',
                        title: 'Tags Available<button class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button>',
                        html: true,
                        trigger: 'click',
                        content: $('#list-form')
                    });
                    this.$el.find('a[name=editPopover]').each(function () {
                        $(this).popover({
                            title: 'Edit&nbsp;<button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button>',
                            html: true,
                            trigger: 'click',
                            content: $('#display-name').clone()
                        }).click(function (event) {
                            that = $(this);
                            close = $(this).data('popover').tip().find('button[name=close]');
                            close.unbind();
                            close.on('click', function (event) {
                                $(that).popover('hide');
                            });
                        });
                    });
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
                            $(popover).data('popover').options.content.find('input[name=datepicker]').datepicker();
                            close = $(popover).data('popover').$tip.find('button[name=close]');
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
                    this._rendered = true;
                },
                render: function () {
                    if (this.beforeRender !== $.noop) { this.beforeRender(); }

                    var $header, $body, vmData,
                        template = _.template(this.template),
                        data = this.collection.toJSON()[0],
                        tagData = this.tagcollection.toJSON();

                    if (data && data.is_vm) {
                        this.navigation = new tabNav.View({
                            tabs: [
                                {text: 'Patching', href: 'nodes/' + this.id + '/patches'},
                                {text: 'VMware', href: 'nodes/' + this.id + '/vmware'}
                            ]
                        });
                        vmData = this.vmcollection.toJSON()[0];
                        this.vm_name = vmData ? vmData.vm_name : null;
                    } else {
                        this.navigation = new tabNav.View({
                            tabs: [
                                {text: 'Patching', href: 'nodes/' + this.id + '/patches'}
                            ]
                        });
                        vmData = null;
                    }

                    this.$el.html('');

                    this.$el.append(template({model: data, tags: tagData, vm: vmData}));

                    $header = this.$el.find('.tab-header');
                    $header.addClass('tabs').html(this.navigation.render().el);

                    $body = this.$el.find('.tab-body');

                    patchesView.Collection = patchesView.Collection.extend({id: this.id});
                    this.patchesView = new patchesView.View({
                        el: $body
                    });
                    this.navigation.setActive('nodes/' + this.id + '/patches');
                    this.showLoading('.tab-body');
                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                showLoading: function (el) {
                    var $el = this.$el,
                        $div = $el.find(el);
                    this._pinwheel = new app.pinwheel();
                    $div.empty().append(this._pinwheel.el);
                },
                stackedAreaGraph: function () {
                    var id = this.id,
                        installedGraph = '#installedGraph',
                        availableGraph = '#availableGraph',
                        $graphDiv = this.$el.find(installedGraph),
                        width = $graphDiv.width(),
                        height = $graphDiv.parent().height(),
                        stackedChart = app.chart.stackedArea().width(width).height(height);
                        //data = this.graphcollection.toJSON();
                    this.showLoading(installedGraph);
                    this.showLoading(availableGraph);
                    d3.json("../api/node/graphs/severity?nodeid=" + id + "&installed=true", function (json) {
                        d3.select(installedGraph).datum([json]).call(stackedChart.title('Installed packages over time'));
                    });
                    d3.json("../api/node/graphs/severity?nodeid=" + id + "&installed=false", function (json) {
                        d3.select(availableGraph).datum([json]).call(stackedChart.title('Available packages over time'));
                    });
                    /*if (data.length) {
                        d3.select(graphId).datum(data).call(stackedChart);
                    }*/
                },
                changeView: function (event) {
                    event.preventDefault();
                    var $tab = $(event.currentTarget),
                        view = $tab.attr('href'),
                        $body = this.$el.find('.tab-body'),
                        id = this.id;
                    if (this._currentTab !== view) {
                        this._currentTab  = view;
                        this.showLoading('.tab-body');
                        if (view === '#nodes/' + id + '/patches') {
                            if (this.patchesView) {
                                this.patchesView.render();
                            } else {
                                patchesView.Collection = patchesView.Collection.extend({id: id});
                                this.patchesView = new patchesView.View({
                                    el: $body
                                });
                            }
                            this.navigation.setActive('nodes/' + id + '/patches');
                        } else if (view === '#nodes/' + id + '/vmware') {
                            if (this.vmView) {
                                this.vmView.render();
                            } else {
                                vmView.Collection = vmView.Collection.extend({id: id});
                                this.vmView = new vmView.View({
                                    el: $body
                                });
                            }
                            this.navigation.setActive('nodes/' + id + '/vmware');
                        }
                    }
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
                                that.$el.find('.alert').first().removeClass('alert-error').addClass('alert-success').show().find('span').html('Operation sent.');
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
                                that.$el.find('.alert').first().removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
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
                showEditOperation: function (event) {
                    var popover = $(event.currentTarget).data('popover'),
                        button = popover.tip().find('button[name=editProperty]');
                    button.unbind();
                    button.on('click', {view: this, popover: popover}, this.submitNameOperation);
                    return false;
                },
                submitNameOperation: function (event) {
                    var $em, $span, params, url,
                        $displayName = $(event.currentTarget).siblings('input'),
                        node_id = event.data.view.collection.id,
                        popover = event.data.popover,
                        operation = popover.$element.attr('id'),
                        $displayNameDiv = $(event.currentTarget).parents('dd');
                    if (operation === 'editDisplay') {
                        params = {
                            nodeid: node_id,
                            displayname: $displayName.val() || 'None'
                        };
                        url = 'api/node/modifyDisplayName';
                    } else if (operation === 'editHost') {
                        params = {
                            nodeid: node_id,
                            hostname: $displayName.val() || 'None'
                        };
                        url = 'api/node/modifyHostName';
                    }
                    $.post(url, params, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            $em = $displayNameDiv.find('em');
                            $span = $displayNameDiv.find('span');
                            if ($em.length !== 0) {
                                $em.remove();
                                $span.remove();
                                if ($displayName.val()) {
                                    $displayNameDiv.prepend('<span>' + $displayName.val() + '</span>');
                                } else {

                                    $displayNameDiv.prepend('<em>Not listed</em>');
                                }
                            }
                            if ($span) { $span.html($displayName.val() || '<em>Not listed</em>'); }
                            popover.hide();
                        }
                    });
                },
                showTags: function (evt) {
                    var showInput, addTag, tagList, close,
                        popover = $(evt.currentTarget).data('popover');
                    if (popover) {
                        showInput = popover.$tip.find('button[name=showNewTag]');
                        close = popover.$tip.find('button[name=close]');
                        addTag = showInput.siblings('div').children('button');
                        tagList = popover.$tip.find('input[name=taglist]');
                        close.bind('click', function () {
                            $(evt.currentTarget).popover('hide');
                        });
                        tagList.unbind().bind('click', this.toggleTag);
                        addTag.unbind().bind('click', this.createTag);
                        showInput.show().siblings('div').hide();
                        showInput.unbind().bind('click', function () {
                            $(this).hide().siblings('div').show();
                        });
                    }
                    return false;
                },
                createTag: function (evt) {
                    var params, tag, user, nodes, operation, checkboxlist, itemstring, tagname,
                        $alert = this.$el.find('.alert').first(),
                        that = this;
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
                                tagname = tag;
                                tag = 'value="' + tag + '"';
                                itemstring = '<div class="item clearfix">' +
                                                '<label class="checkbox">' + tagname +
                                                    '<input name="taglist" type="checkbox" checked="checked" ' + tag + '/>' +
                                                '</label>' +
                                            '</div>';
                                checkboxlist.append(itemstring);
                                checkboxlist.find('input[name=taglist]').on('click', that.toggleTag);
                                that.tagcollection.fetch();
                                that.collection.fetch();
                                $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html('Tag ' + tagname + ' was created.');
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                    return false;
                },
                toggleTag: function (evt) {
                    var params, nodes, tag, user, list,
                        checked = evt.currentTarget.checked,
                        $el = this.$el,
                        $alert = $el.find('.alert').first(),
                        that = this;
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
                        params.operation = 'add_to_tag';
                        $.post("/api/tagging/addTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    that.tagsinnodecollection.fetch();
                                    $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html('Tag ' + tag + ' was applied.');
                                } else {
                                    $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                                }
                            });
                    } else {
                        //remove node from tag
                        params.operation = 'remove_from_tag';
                        $.post("/api/tagging/removeTagPerNode", { operation: JSON.stringify(params) },
                            function (json) {
                                window.console.log(json);
                                if (json.pass) {
                                    that.tagsinnodecollection.fetch();
                                    $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html('Tag ' + tag + ' was removed.');
                                } else {
                                    $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                                }
                            });
                    }
                },
                removeTag: function (event) {
                    var $button = $(event.currentTarget),
                        tag = $button.attr('value'),
                        $alert = this.$el.find('.alert').first(),
                        node = $button.data('node'),
                        user = window.User.get('name'),
                        that = this,
                        params = {
                            operation: 'remove_from_tag',
                            nodes: [node],
                            user: user,
                            tag: tag
                        };
                    console.log(params);
                    $.post("/api/tagging/removeTagPerNode", { operation: JSON.stringify(params) },
                        function (json) {
                            window.console.log(json);
                            if (json.pass) {
                                that.collection.fetch();
                                $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html('Tag ' + tag + ' was removed.');
                            } else {
                                $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                            }
                        });
                },
                updateTagList: function () {
                    var $item, $leftDiv, $rightDiv, $tagSpan, $removeButton, $href,
                        $okIcon, $rebootIcon, $downIcon, $trashIcon,
                        $items = this.$el.find('#tagItems'),
                        data = this.tagsinnodecollection.toJSON()[0],
                        tags = data.tags,
                        that = this,
                        newElement = function (element) {
                            return $(document.createElement(element));
                        };
                    $items.empty();
                    _.each(tags, function (tag) {
                        $item       = newElement('div').addClass('item row-fluid');
                        $leftDiv    = newElement('div').addClass('span6');
                        $rightDiv   = newElement('div').addClass('span6 alignRight');
                        $tagSpan = newElement('span').addClass('label label-info').html('<i class="icon-tag"></i>&nbsp;' + tag.tag_name);
                        $leftDiv.append($tagSpan, '&nbsp;');
                        if (tag.agents_up > 0) {
                            $okIcon = newElement('i').addClass('icon-ok').attr('title', tag.agents_up + ' agents up.').data('placement', 'right').css('color', 'green');
                            $leftDiv.append($okIcon, '&nbsp;');
                        }
                        if (tag.reboots_pending > 0) {
                            $rebootIcon = newElement('i').addClass('icon-warning-sign').attr('title', tag.reboots_pending + 'reboots pending..').data('placement', 'right').css('color', 'orange');
                            $leftDiv.append($rebootIcon, '&nbsp;');
                        }
                        if (tag.agents_down > 0) {
                            $downIcon = newElement('i').addClass('icon-warning-sign').attr('title', tag.agents_down + ' agents down.').data('placement', 'right').css('color', 'red');
                            $leftDiv.append($downIcon);
                        }
                        $removeButton = newElement('button').addClass('btn btn-link noPadding').attr({
                            name: 'removeTag',
                            value: tag.tag_name
                        }).data('node', that.id);
                        $trashIcon = newElement('i').addClass('icon-trash').attr('title', 'RemoveTag').data('placement', 'left').css('color', 'red');
                        $href = newElement('a').attr('href', '#tags/' + tag.tag_id).html('More Info');
                        $rightDiv.append($removeButton.append($trashIcon), $href);
                        $item.append($leftDiv, $rightDiv);
                        $items.append($item);
                    });
                    $items.find('i').each(function () {
                        $(this).tooltip();
                    });
                },
                showNetworking: function (event) {
                    var $button = $(event.currentTarget),
                        $hidden = $button.parent().siblings('.hidden');
                    if ($button.html() === 'Show more') {
                        $button.html('Show less');
                    } else {
                        $button.html('Show more');
                    }
                    $hidden.toggle();
                },
                agentOperation: function (event) {
                    var $button = $(event.currentTarget),
                        $alert = this.$el.find('.alert').first(),
                        operation = $button.data('value'),
                        url = 'submitForm',
                        nodeId = this.id,
                        params = {
                            node: nodeId,
                            operation: operation
                        };
                    window.console.log(params);
                    $.post(url, params, function (json) {
                        window.console.log(json);
                        if (json.pass) {
                            $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html(json.message);
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
                    /*
                    switch (operation) {
                    case 'start':
                        window.console.log('start here');
                        break;
                    case 'stop':
                        window.console.log('stop here');
                        break;
                    case 'restart':
                        window.console.log('restart here');
                        break;
                    }
                    */
                },
                nodeOperation: function (event) {
                    var url, $button = $(event.currentTarget),
                        $alert = this.$el.find('.alert').first(),
                        operation = $button.data('value'),
                        vmName = this.vm_name,
                        params = {
                            vm_name: vmName
                        };
                    window.console.log(params);
                    if (operation === 'start') {
                        url = 'api/virtual/node/poweron';
                    } else if (operation === 'stop') {
                        url = 'api/virtual/node/shutdown';
                    } else if (operation === 'restart') {
                        url = 'api/virtual/node/reboot';
                    }
                    $.post(url, params, function (json) {
                        if (json.pass) {
                            $alert.removeClass('alert-error').addClass('alert-success').show().find('span').html(json.message);
                        } else {
                            $alert.removeClass('alert-success').addClass('alert-error').show().find('span').html(json.message);
                        }
                    });
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
