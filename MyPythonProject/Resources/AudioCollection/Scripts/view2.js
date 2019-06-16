"use strict";
var root = root || "/audiocollection/";
var website = website || {};


(function (publics) {

    function appendbutton(parent, element, text) {
        var button = document.createElement("button");
        var textButton = document.createTextNode(text);
        button.className = "button";
        button.type = "button";
        button.id = text;
        button.appendChild(textButton);
        parent.insertBefore(button, element);
    }

    publics.initialize = function() {

        // -----
        var anchor,
            anchorText,
            key,
            browser;
        var paths = window.location.pathname.split("/");
        var pathname = paths[paths.length - 1];
        var search = window.location.search;
        if (search !== "") {
            browser = document.querySelector("div.browser");
            anchor = document.createElement("a");
            anchorText = document.createTextNode("All");
            anchor.href = root + pathname;
            key = search.split("=")[0];
            switch (key) {
                case "?artistsort":
                    anchor.title = "afficher tous les artistes";
                    break;
                case "?genre":
                    anchor.title = "afficher tous les genres";
                    break;
                case "?month":
                    anchor.title = "afficher tous les mois";
                    break;
                case "?year":
                    anchor.title = "afficher toutes les années";
            }
            anchor.appendChild(anchorText);
            browser.insertBefore(anchor, document.querySelector("div.browser > a"));
        }

        // -----
        var buttons = [];
        var i,
            len;
        var view = $("div#wrapper").attr("class");
        switch (view) {
            case "artists":
                buttons = ["genres", "months", "years"];
                break;
            case "genres":
                buttons = ["artists", "months", "years"];
                break;
            case "months":
                buttons = ["artists", "genres", "years"];
                break;
            case "years":
                buttons = ["artists", "months", "months"];
        }
        if (buttons) {
            for (i = 0, len = 3; i < len; i++) {
                appendbutton(document.querySelector("div#div2").firstElementChild, document.querySelector("#refresh"), buttons[i]);
            }
        }

    };

    publics.browse = function() {
        var month;

        $("div.browser > a").hover(function() {
            $("div.browser > a").each(function() {
                if ($(this).hasClass("bold")) {
                    month = $(this).text();
                }
            });
            $("div.browser > a").removeClass().addClass("hover");
            $(this).removeClass().addClass("bold");
        },
        function() {
            $("div.browser > a").removeClass();
            $("div.browser > a").filter(function() {
                return $(this).text() === month;
            }).addClass("bold");
        });

    };

    publics.init = function() {
        website.view2.initialize();
        website.view2.browse();
    };

})(website.view2 = {});
