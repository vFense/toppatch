define(
    ['jquery', 'backbone', 'test-json/patchLoader'],
    function ($, Backbone, patchList) {
        "use strict";

        var ipTable = _.shuffle(_.range(2, 254)),
            ipAvailable = 0,
            osList = [
                { name: 'Windows 7', short: "win7" },
                { name: 'Windows Server 2008', short: "win2k8" },
                { name: 'Windows Vista', short: "winV" },
                { name: 'Windows Server 2003', short: "win2k3" },
                { name: 'Windows XP', short: "winXP" }
            ],
            node,
            nodes;

        node = Backbone.Model.extend({
            defaults: {
                patches: {
                    need: [],
                    patched: [],
                    failed: []
                }
            },
            initialize: function () {
                this.ip = this.ip || (function () {
                    var temp = ipTable[ipAvailable];
                    ipAvailable += 1;
                    return temp;
                }());

                this.os = this.os || _.shuffle(osList)[0];

                var myPatches = patchList[this.os.short].patches,
                    pick = Math.ceil(Math.random() * myPatches.length);

                if (!this.patches) { this.patches = {}; }
                this.patches.need = _.first(myPatches, pick);
                this.patches.patched = _.rest(myPatches, pick);
            }
        });

        nodes = new (Backbone.Collection.extend({
            model: node
        }))(
            // Initialize the collection with a
            // random length array of empty objects
            (function () {
                var i, q,
                    out = [],   // Our array
                    min = 5,    // Minimum length of array
                    max = 15;   // Maximum length of array
                for (i = 0, q = _.shuffle(_.range(min, max))[0]; i < q; i += 1) {
                    out.push({});
                }
                return out;
            }())
        );


        console.log({nodes: nodes});

        return nodes;
        /*  nodes.json
            [
                {
                    "ip": "192.168.1.2",
                    "os": "Windows 7",
                    "patches": {
                        "need": [
                            "KB0000001",
                            "KB0000002",
                            etc...
                        ],
                        "complete": [],
                        "failed": []
                    }
                },
                etc...
            ]
         */
    }
);