/**
 * Created with PyCharm.
 * User: parallels
 * Date: 9/14/12
 * Time: 1:15 AM
 * To change this template use File | Settings | File Templates.
 */
require(['jquery', 'backbone', 'app', 'jquery.ui', 'jquery.bootstrap'], function($, Backbone, app) {

    var User = Backbone.Model.extend({
        defaults: {
            config: {
                name: "Guest",
                access: {
                    patches: true
                },
                textWidgets: 4,
                textKey: ["Nodes", "Patched", "Scheduled Patches", "Failed Patches"],
                graphWidgets: 3,
                graphKey: ["pie", "bar", "line"],
                classType: ["info", "success", "warning", "error"],
                getData: [ globalData.get("nodeData").Nodes, globalData.get("nodeData").Patched, globalData.get("nodeData").Pending, globalData.get("nodeData").Failed]
            }
        },
        initialize: function() {
            //$('#account-dropdown').html(_.template(TEMPLATES["account/dropdownMenu"](), this.get("config")));
            //$('#dashboardNav').html(_.template(TEMPLATES["dashboard/navigation"](), this.get("config")));
            /*
             for(var i = 0; i < 4; i++){
             var variables = {
             widget: "text" + i,
             span: "span3",
             title: this.get("config").textKey[i],
             type: this.get("config").classType[i],
             data: this.get("config").getData[i]
             };
             var template = _.template($("#text_template").html(), variables);
             $("#summary").append(template);
             }
             */
        }
    });
    var user = new User();


    $("#deploy").click(function () {
        var data = [{ "date": new Date(), "name": "Security Update for Microsoft XML Editor 2010 (KB2251489)" },
            { "date": new Date(), "name": "Security Update for Microsoft Visual C++ 2008 Service Pack 1 Redistributable Package (KB2538243)" },
            { "date": new Date(), "name": "Security Update for Microsoft Visual Studio 2010 (KB2542054)" },
            { "date": new Date(), "name": "Security Update for Microsoft Visual Studio 2008 Service Pack 1 (KB2669970)" },
            { "date": new Date(), "name": "Update for Microsoft Tools for Office Runtime Redistributable (KB2525428)" },
            { "date": new Date(), "name": "Security Update for Microsoft .NET Framework 4 on XP, Server 2003, Vista, Windows 7, Server 2008, Server 2008 R2 for x64 (KB2604121)" },
            { "date": new Date(), "name": "Microsoft Security Essentials - KB2691894" },
            { "date": new Date(), "name": "Security Update for Windows 7 for x64-based Systems (KB2731847)" }];
        var variables = { type: "patches", data: data };
        //var template = _.template($("#patch_template").html(), variables);
        //$("#dashboard-view").html(template);
    });
    jQuery(document).ready(function($) {
        //window.ready = function() {
        //$("#something").buttonset();
        //$('#something').buttonset('refresh');

        /*
        $("#size").buttonset();
        $("#graphType").buttonset();
        $("#graphdata").buttonset();

        $("#parameter").buttonset();
        */

        var table = app.chart.generateTable().headerRow(true)
        .sort(function (a, b) {
            return a.score - b.score;
         });
        var data = [{"vendor":"mozilla","product":"firefox","version":"8.0:--:--","cveid":"CVE-2011-3658","score":"7.5"},{"vendor":"mozilla","product":"firefox","version":"8.0:--:--","cveid":"CVE-2012-0451","score":"4.3"},{"vendor":"mozilla","product":"firefox","version":"8.0:--:--","cveid":"CVE-2012-0454","score":"7.5"},{"vendor":"mozilla","product":"firefox","version":"8.0:--:--","cveid":"CVE-2012-0455","score":"4.3"},{"vendor":"mozilla","product":"firefox","version":"8.0:--:--","cveid":"CVE-2012-0456","score":"5.0"}];
        d3.select("#data").datum(data).call(table);
        //};
    });
});