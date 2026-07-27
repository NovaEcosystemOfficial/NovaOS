/************
 * NovaOS desktop layout — wallpaper only, no Plasma panels.
 * Top chrome is Nova Shell Top Bar 3.0 (glass strut panel).
 ************/

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image";
}

// Do NOT loadTemplate("org.kde.plasma.desktop.defaultPanel")
// Nova Top Bar replaces Plasma panels.
