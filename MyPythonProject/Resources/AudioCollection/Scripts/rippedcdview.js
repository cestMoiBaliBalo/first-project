"use strict";
var website = website || {};


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var privates = {};


    //     ----------------
    //  4. Initialize page.
    //     ----------------
    privates.initialize = function() {

        // -----
        var div1,
            div2,
            text,
            button;

        // ----- Insert "refresh" button.
        //       No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        div1 = document.querySelector("#div1");
        // -----
        text = document.createTextNode("Refresh");
        button = document.createElement("button");
        div2 = document.createElement("div");
        // -----
        button.type = "button";
        button.id = "refresh";
        button.className = "button";
        div2.id = "div2";
        // -----
        button.appendChild(text);
        div2.appendChild(button);
        div1.parentNode.appendChild(div2);

    };


    //     -------------
    //  5. Refresh page.
    //     -------------
    privates.refresh = function() {
        $("#container").on("click", "#refresh", function() {
            var $postdata = $.get("/audiocollection/refreshrippedcd");
            $postdata.done(function() {
                $(location).attr("href", "/" + window.location.href.split("/")[3] + "/" + window.location.href.split("/")[4]);
            });
        });
    };


    //     ----------------
    // 11. Page controlers.
    //     ----------------
    publics.init = function() {
        privates.initialize();
        privates.refresh();
    };


})(website.rippedcdview = {});