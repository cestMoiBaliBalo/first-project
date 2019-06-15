"use strict";
var root = root || "/audiocollection/";
var website = website || {};


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var coversperpage = 32,
        privates = {};
    var month;



    //     -------------
    //  2. Set mappings.
    //     -------------
    var mapping = {"/audiocollection/digitalalbumsview": "digitalalbums",
                   "/audiocollection/rippeddiscsview": "rippeddiscs"};


    //     --------------------
    //  2. Set inner functions.
    //     --------------------


    //  2.1. Show/Hide "more covers" button.
    function more_button() {
        var div_buttons = document.querySelector("#buttons"),
            button_less = document.querySelector("#less"),
            container = document.querySelector("#container"),
            text;

        // Get displayed total covers number.
        var covers = document.querySelectorAll(".cover");

        // Is "more covers" button already defined?
        var button_more = document.querySelector("#more");

        // Show "more covers" button.
        // Only if both at least one cover is displayed and "more covers" button isn't already defined.
        if (covers.length && !button_more) {

            if (!div_buttons) {
                div_buttons = document.createElement("div");
                div_buttons.id = "buttons";
                container.appendChild(div_buttons);
            }
            button_more = document.createElement("button");
            button_more.className = "button";
            button_more.type = "button";
            button_more.id = "more";
            text = document.createTextNode("More covers");
            button_more.appendChild(text);
            if (!button_less) {
                div_buttons.appendChild(button_more);
                return;
            }
            div_buttons.insertBefore(button_more, button_less);
            return;

        }

    }


    //  2.2. Show/Hide "less covers" button.
    function less_button() {

        var div_buttons = document.querySelector("#buttons"),
            text;

        // Get displayed total covers number.
        var covers = document.querySelectorAll(".cover");

        // Is "less covers" button already defined?
        var button_less = document.querySelector("#less");

        // Show "less covers" button.
        // Only if both at least covers per page number is exceeded and "less covers" button isn't already defined.
        if (covers.length > coversperpage && !button_less) {
            button_less = document.createElement("button");
            button_less.className = "button";
            button_less.type = "button";
            button_less.id = "less";
            text = document.createTextNode("Less covers");
            button_less.appendChild(text);
            div_buttons.appendChild(button_less);
            return;
        }

        // Hide "less covers" button if covers per page number is not exceeded.
        if (covers.length <= coversperpage && button_less) {
            button_less.parentNode.removeChild(button_less);
            return;
        }

    }


    //  2.3. Show/Hide "all covers" button.
    function all_button() {
        var div_buttons = document.querySelector("#buttons"),
            button_more = document.querySelector("#more"),
            button_less = document.querySelector("#less"),
            container = document.querySelector("#container"),
            text;

        // Get displayed total covers number.
        var covers = document.querySelectorAll(".cover");

        // Is "all covers" button already defined?
        var button_all = document.querySelector("#all");

        // Show "all covers" button.
        // Only if both at least one cover is displayed and "all covers" button isn't already defined.
        if (covers.length && !button_all) {

            if (!div_buttons) {
                div_buttons = document.createElement("div");
                div_buttons.id = "buttons";
                container.appendChild(div_buttons);
            }
            button_all = document.createElement("button");
            button_all.className = "button";
            button_all.type = "button";
            button_all.id = "all";
            text = document.createTextNode("All covers");
            button_all.appendChild(text);
            if (button_more) {
                div_buttons.insertBefore(button_all, button_more);
                return;
            }
            if (button_less) {
                div_buttons.insertBefore(button_all, button_less);
                return;
            }
            div_buttons.appendChild(button_all);
            return;
        }

    }


    //  2.4. Change URL hash part when more covers are requested.
    function displaymorecovers() {
        location.hash = document.querySelectorAll(".cover").length + 1;
    }


    //  2.5. Change URL hash part when less covers are requested.
    function displaylesscovers() {
        var covers = document.querySelectorAll(".cover");
        var modulo = covers.length % coversperpage;
        switch (modulo) {
            case 0:
                location.hash = covers.length - 2 * coversperpage + 1;
                break;
            default:
                location.hash = covers.length - modulo - coversperpage + 1;
        }
    }


    //  2.6. Change URL hash part when all covers are requested.
    function displayallcovers() {
        location.hash = 9999;
    }


    //  2.7. Get number of covers.
    function coverid(collection, prefix, from) {
        var i,
            j,
            id,
            length;

        if (!from) {
            from = 1;
        }
        j = from;
        for (i = 0, length = collection.length; i < length; i++) {
            id = j.numberToText().lPadding(4, "0");
            collection[i].id = id.substr(id.length - 4, 4);
            if (prefix) {
                collection[i].id = prefix + collection[i].id;
            }
            j++;
        }

    }


    //     ----------------
    //  3. Initialize page.
    //     ----------------
    publics.initialize = function() {
        var browse,
            buttons,
            div2,
            div_buttons,
            text,
            view;
        var paths = window.location.pathname.split("/");
        var pathname = paths[paths.length - 1];

        //  3.1. Insert "browse" button for browsing ripped discs.
        if (pathname === "rippeddiscsview") {
            div2 = document.querySelector("#div2");
            div_buttons = div2.getElementsByTagName("div")[0];
            browse = document.createElement("button");
            text = document.createTextNode("Browse");
            browse.className = "button";
            browse.type = "button";
            browse.id = "browse";
            browse.appendChild(text);
            div_buttons.insertBefore(browse, document.getElementById("refresh"));
        }

        //  3.2. Insert both "more covers" and "less covers" button.
        //       Only if view is "default".
        //       No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        view = document.getElementById("view");
        if (view.options[view.selectedIndex].value === "default") {
            more_button();
            less_button();
            all_button();
        }

        //  3.3. Get number of covers.
        coverid(document.querySelectorAll(".cover"), "cover_");

        //  3.3. Configure events listeners.
        buttons = document.getElementById("buttons");
        if (buttons) {
            buttons.addEventListener("click", function(e) {
                if (e.target) {
                    switch (e.target.id.toLowerCase()) {
                        case "less":
                            displaylesscovers();
                            break;
                        case "more":
                            displaymorecovers();
                            break;
                        case "all":
                            displayallcovers();
                            break;
                    }
                }
            });
        }

        //  3.4. Display more, or less, covers by getting URL hash part.
        //       Allow to browse covers with browser history.
        window.onhashchange = function() {
            var $posting,
                hash,
                i,
                number,
                pathname;

            pathname = window.location.pathname;

            //  3.4.a. Get required HTML elements.
            var more = document.querySelector("#more"),
                less = document.querySelector("#less"),
                all = document.querySelector("#all");

            //  3.4.b. Get first displayed cover number.
            hash = parseInt(location.hash.replace("#", ''), 10);
            if (!hash) {
                number = 1;
            }
            if (hash === 9999) {
                number = 1;
            }
            if (!number) {
                number = hash;
            }

            //  3.4.c. Get displayed covers count.
            var covers = document.querySelectorAll(".cover");

            //  3.4.d. Remove displayed covers from first cover number to covers count.
            if (covers) {
                i = number;
                while (i <= covers.length) {
                    var cover = covers[i++ - 1];
                    if (cover) {
                        cover.parentNode.removeChild(cover);
                    }
                }
            }

            // 3.4.e. Append requested covers when more covers are requested.
            //        Show or hide both "more covers" and less covers" buttons.
            switch (hash) {
                case 9999:
                    $posting = $.get(root + "getcovers?collection=" + mapping[pathname] + "&coversperpage=9999");
                    break;
                default:
                    $posting = $.get(root + "getcovers?collection=" + mapping[pathname] + "&start=" + (number - 1));
            }
            $posting.done(function(r1) {

                $posting = $.get(root + "gettotalitems?collection=" + mapping[pathname]);
                $posting.done(function(r2) {

                    // -----
                    switch (number) {
                        case 1:
                            $(r1.covers).insertAfter($("#h2-title"));
                            break;
                        default:
                            $(r1.covers).insertAfter($(".cover:last"));
                    }

                    // -----
                    var collection = $(".cover:not([id])");
                    if (collection.length) {
                        covers = $(".cover[id]");
                        var from = 1;
                        if (covers.length) {
                            from = parseInt(covers.last().attr("id").split("_")[1], 10) + 1;
                        }
                        coverid(collection, "cover_", from);
                    }

                    // -----
                    covers = document.querySelectorAll(".cover");

                    // -----
                    if (!less && covers.length > coversperpage) {
                        less_button();
                    }
                    if (less && covers.length <= coversperpage) {
                        less.parentNode.removeChild(less);
                    }

                    // -----
                    if (!more && covers.length < r2.covers) {
                        more_button();
                    }
                    if (more && covers.length >= r2.covers) {
                        more.parentNode.removeChild(more);
                    }

                    // -----
                    if (!all && covers.length < r2.covers) {
                        all_button();
                    }
                    if (all && covers.length >= r2.covers) {
                        all.parentNode.removeChild(all);
                    }

                });

            });

        };

    };


    //     -------------------
    //  4. Change covers view.
    //     -------------------
    publics.changecoversview = function() {
        $("#view").change(function() {
            $("form").submit();
        });
    };


    //     --------------------
    //  5. Browse ripped discs.
    //     --------------------
    publics.browse = function() {
        $("#browse").click(function() {
            $(location).attr("href", root + "rippeddiscsviewbymonth");
        });
    };



    //     ----------------
    //  6. Page controlers.
    //     ----------------
    publics.init = function() {
        website.view1.initialize();
        website.view1.changecoversview();
        website.view1.browse();
    };


})(website.view1 = {});
