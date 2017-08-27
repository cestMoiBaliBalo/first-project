"use strict";
var website = website || {};


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var privates = {};


    //     --------------------
    //  2. Set inner functions.
    //     --------------------
    function getcover(event) {
        /* jshint validthis: true */

        if (event) {

            var cover,
                innercover,
                image,
                firstscript,
                albumid,
                albumsort;

            switch (event.type) {


                // MOUSEOVER.
                case "mouseover":

                    //  2.1 Append "hover" class to the hovered album.
                    this.classList.toggle("hover");

                    //  2.2. Set cover source for the hovered album.
                    albumid = this.children[3].children[0].href;
                    albumsort = albumid.split("=")[1].split("&")[0].split(".");

                    //  2.3. Show hovered album cover.

                    //  2.3.a. Define HTML structure.
                    firstscript = document.querySelectorAll("script")[0];
                    cover = document.createElement("div");
                    innercover = document.createElement("div");
                    image = document.createElement("img");

                    //  2.3.b. Define HTML structure attributes.
                    cover.id = "cover";
                    innercover.id = "innercover";
                    image.src = "albumart/" + albumsort[0] + "/" + albumsort[1] + "/" + albumsort[2] + "." + albumsort[3] + "." + albumsort[4] + "/iPod-Front.jpg";
                    image.alt = "No cover found!";
                    image.width = "150";
                    image.height = "150";

                    //  2.3.c. Append HTML structure to the DOM.
                    innercover.appendChild(image);
                    cover.appendChild(innercover);
                    firstscript.parentNode.insertBefore(cover, firstscript);

                    // -----
                    break;


                    // MOUSEOUT.
                case "mouseout":

                    //  2.4. Remove "hover" class from the hovered album.
                    this.classList.toggle("hover");

                    //  2.5. Remove HTML structure from the DOM.
                    cover = document.querySelector("#cover");
                    if (cover) {
                        cover.parentNode.removeChild(cover);
                    }

                    // -----
                    break;


            }

        }

    }


    //     ----------------
    //  3. Initialize page.
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

        // ----- Get album cover.
        var albums = document.querySelectorAll(".default");
        for (var i = 0, len = albums.length; i < len; i++) {
            albums[i].addEventListener("mouseover", getcover);
            albums[i].addEventListener("mouseout", getcover);
        }

    };


    //     -------------
    //  5. Refresh page.
    //     -------------
    privates.refresh = function() {
        $("#refresh").on("click", function() {
            var $postdata = $.get("/audiocollection/refreshdigitalalbums");
            $postdata.done(function() {
                $(location).attr("href", "/audiocollection/digitalalbums_view?page=" + $("#container").find("#pages").children("b").text());
            });
        });
    };


    //     --------------------
    //  6. Control form events.
    //     --------------------
    privates.formcontroler = function() {

        //  5.1. Enable both "submit" and "reset" button once a radio button or checkbox is checked.
        $("#digitalalbums-form").find("td").children(":checkbox").on("change", function() {
            $("#digitalalbums-form").children("input").prop({
                disabled: false
            }).removeClass("no-cursor");
        });

        //  5.2. Disable both "submit" and "reset" button once "reset" is pressed.
        $("#digitalalbums-form").children(":reset").on("click", function() {
            $("#digitalalbums-form").children("input").prop({
                disabled: true
            }).addClass("no-cursor");
        });

        //  5.3. All checkboxes must be checked if "All" is checked.
        //       All checkboxes must be unchecked if "All" is unchecked.
        $("#select-all").on("click", function() {
            var ischecked = $(this).is(":checked");
            $("#digitalalbums-form").find("tr:has(td)").find("input").prop("checked", ischecked);
            if (ischecked) {
                $("#digitalalbums-form").children("input").prop({
                    disabled: false
                }).removeClass("no-cursor");
            }
            if (!ischecked) {
                $("#digitalalbums-form").children("input").prop({
                    disabled: true
                }).addClass("no-cursor");
            }
        });

        $("#digitalalbums-form").find("tr:has(td)").find("input").on("change", function() {

            //  5.3.a. "All" must be unchecked as soon as one checkbox is unchecked.
            var ischecked = $(this).is(":checked");
            if (!ischecked) {
                $("#select-all").prop("checked", false);
            }

            // "All" must be checked if all checkboxes are checked.
            var $albums = $("#digitalalbums-form").find("tr:has(td)");
            var total_boxes = $albums.find("input").length;
            var checked_boxes = $albums.find("input:checked").length;
            if (total_boxes === checked_boxes) {
                $("#select-all").prop("checked", true);
            }

            //  5.3.b. Disable both "submit" and "reset" button once all checkboxes are unchecked.
            if (checked_boxes === 0) {
                $("#digitalalbums-form").children("input").prop({
                    disabled: true
                }).addClass("no-cursor");
            }

        });

        //  5.4. Control submit event.
        $("#digitalalbums-form").submit(function(event) {
            event.preventDefault();
            var $checkboxes = $(this).find("tr:has(td)").find("input").filter(":checked");
            var rowid = [];
            $checkboxes.each(function() {
                rowid.push(this.id.split("-")[1]);
            });
            if (rowid.length > 0) {
                var $posting = $.post("/audiocollection/update_digitalalbums_playeddate", JSON.stringify({
                    "rows": rowid
                }));
                $posting.done(function() {
                    $.get("/audiocollection/refreshdigitalalbums");
                    $checkboxes.prop({
                        checked: false
                    });
                });
            }
        });

    };


    //     ----------------
    //  7. Page controlers.
    //     ----------------
    publics.init = function() {
        privates.initialize();
        privates.formcontroler();
        privates.refresh();
    };


})(website.digitalalbums = {});