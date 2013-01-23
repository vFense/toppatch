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
            GraphCollection: Backbone.Collection.extend({
                baseUrl: 'api/patches.json',
                url: function () {
                    return this.baseUrl + '?nodeid=' + this.id + '&status=installed&count=50&offset=0';
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    _.bindAll(this, 'createtag');
                    this.template = myTemplate;
                    this.collection = new exports.Collection();
                    this.collection.bind('reset', this.render, this);
                    this.collection.fetch();

                    this.id = this.collection.id;

                    this.tagcollection = new exports.TagCollection();
                    this.tagcollection.bind('reset', this.render, this);
                    this.tagcollection.fetch();

                    this.vmcollection = new exports.VmCollection();
                    this.vmcollection.bind('reset', this.render, this);
                    this.vmcollection.fetch();

                    this.graphcollection = new exports.GraphCollection();
                    this.graphcollection.bind('reset', this.render, this);
                    this.graphcollection.fetch();

                    this.startWebSocket();
                },
                events: {
                    'click .disabled': function (e) { e.preventDefault(); },
                    'click li a': 'changeView',
                    'click #addTag': 'showtags',
                    'click #createtag': 'createtag',
                    'click button[name=dependencies]': 'showDependencies',
                    'click input[name=taglist]': 'toggletag',
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
                    this.lineGraph();
                    this.$el.find('#addTag').popover({
                        title: 'Tags Available<button type="button" class="btn btn-link noPadding pull-right" id="close"><i class="icon-remove"></i></button>',
                        html: true,
                        trigger: 'click',
                        content: $('#list-form')
                    });
                    this.$el.find('a[name=editPopover]').each(function () {
                        $(this).popover({
                            title: '&nbsp;<button type="button" class="btn btn-link noPadding pull-right" name="close"><i class="icon-remove"></i></button>',
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

                    this.$el.find("a.disabled").on("click", false);

                    if (this.onRender !== $.noop) { this.onRender(); }
                    return this;
                },
                lineGraph: function () {
                    var data = [],
                        graph = '#nodeGraph',
                        lineChart = app.chart.line().width(900),
                        variable = this.graphcollection.toJSON()[0];
                    if (variable) {
                        variable.data.sort(function (a, b) {
                            var keyA = new Date(a.date_installed),
                                keyB = new Date(b.date_installed);
                            // Compare the 2 dates
                            if (keyA < keyB) { return -1; }
                            if (keyA > keyB) { return 1; }
                            return 0;
                        });
                        _.each(variable.data, function (patch, i) {
                            data.push({
                                label: new Date(patch.date_installed).getTime(),
                                value: i + 1,
                                patch_name: patch.name,
                                count: variable.count - variable.data.length
                            });
                        });
                        d3.select(graph).datum(data).call(lineChart);
                    }
                },
                startWebSocket: function (event) {
                    var ws = new window.WebSocket("wss://" + window.location.host + "/ws");
                    ws.onmessage = function (evt) {
                        window.console.log(['websocket', 'message', evt]);
                        var $alert = this.$el.find('.alert').first();
                        //$alert.removeClass('alert-success alert-error').addClass('alert-info').html('message here');
                        window.console.log($alert);
                    };
                    ws.onclose = function (evt) {
                        window.console.log(['websocket', 'closed', evt]);
                    };
                    ws.onopen = function (evt) {
                        window.console.log(['websocket', 'opened', evt]);
                    };
                    ws.onerror = function (evt) {
                        window.console.log(['websocket', 'error', evt]);
                    };
                },
                changeView: function (event) {
                    event.preventDefault();
                    var $tab = $(event.currentTarget),
                        $body = this.$el.find('.tab-body'),
                        id = this.id;
                    if ($tab.attr('href') === '#nodes/' + id + '/patches') {
                        patchesView.Collection = patchesView.Collection.extend({id: id});
                        this.patchesView = new patchesView.View({
                            el: $body
                        });
                        this.navigation.setActive('nodes/' + id + '/patches');
                    } else if ($tab.attr('href') === '#nodes/' + id + '/vmware') {
                        vmView.Collection = vmView.Collection.extend({id: id});
                        this.vmView = new vmView.View({
                            el: $body
                        });
                        this.navigation.setActive('nodes/' + id + '/vmware');
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
