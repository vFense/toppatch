define(
    [
        'test-json/windows2K3Patches',
        'test-json/windows2K8Patches',
        'test-json/windows7Patches',
        'test-json/windowsVistaPatches',
        'test-json/windowsXPPatches'
    ],
    function (win2k3, win2k8, win7, winV, winXP) {
        "use strict";
        return {
            "win2k3": win2k3,
            "win2k8": win2k8,
            "win7": win7,
            "winV": winV,
            "winXP": winXP
        };
    }
);