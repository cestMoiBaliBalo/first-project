"use strict";
var website = website || {},
    correct = "rgba(68, 191, 68, 0.30)",
    incorrect = "rgba(191, 68, 68, 0.30)",
    bydefault = "#E8EEEF",
    focused = "#D2D9DD";


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var $before,
        $after,
        winW = parseFloat(window.innerWidth),
        url = {
            "check": "/audiocollection/checkrippedcdlog",
            "dialogbox": "/audiocollection/getdialogbox",
            "create": "/audiocollection/rippedcdlog",
            "update": "/audiocollection/rippedcdlog",
            "store": "/audiocollection/storerippedcdlog"
        },
        privates = {},
        check = {};


    //     ------------------
    //  2. Set inner objects.
    //     ------------------
    check.artistsort = function(s) {
        return /^[A-Z][^,]+, [A-Z][a-z0-9]+$/.test(s) || /^[A-Z][A-Za-z0-9 ]+$/.test(s);
    };


    check.albumsort = function(s) {
        var rex1 = /^[12]\.(?:19[6789]|20[012])\d(?:0[1-9]|1[0-2])(?:0[1-9]|[12][0-9]|3[01])\.\d$/,
            rex2 = /^[12]\.(?:19[6789]|20[012])\d0000\.\d$/;
        return rex1.test(s) || rex2.test(s);
    };


    check.artist = function(s) {
        console.log(s);
        if (!s) {
            return false;
        }
        var artistsort = $("#artistsort").val(),
            artist = artistsort.replace(/^([A-Z][^,]+), ([A-Z][a-z0-9]+)$/, "$2 $1");
        return s === artistsort || s === artist || s.replace(/^([^&]+)&(.+)$/, "$1").trim() === artist;
    };


    check.year = function(s) {
        return parseInt(s, 10) === parseInt($("#albumsort").val().replace(/^\d\.(\d{4})\d{4}\.\d$/, "$1"), 10);
    };


    check.album = function(s) {
        return /^[A-Z].+$/.test(s);
    };


    check.upc = function(s) {
        return /^\d{12,13}$/.test(s);
    };


    check.application = function(s) {
        return /^(?:dBpoweramp 15\.1)$/.test(s);
    };


    //     --------------------
    //  3. Set inner functions.
    //     --------------------
    function inittagsstyle(action) {

        var i,
            len,
            tags,
            numbers,
            selects;

        // -----
        tags = $("#div3").find("input[type='text']").get();

        // -----
        numbers = $("#div3").find("input[type='number']").get();
        for (i = 0, len = numbers.length; i < len; i++) {
            tags.push(numbers[i]);
        }

        // -----
        selects = $("#div3").find("select").get();
        for (i = 0, len = selects.length; i < len; i++) {
            tags.push(selects[i]);
        }

        // -----
        for (i = 0, len = tags.length; i < len; i++) {

            var style = tags[i].style,
                id = tags[i].id.toLowerCase(),
                value = tags[i].value;

            style.backgroundColor = bydefault;
            if (action === undefined || action.toLowerCase() === "delete") {
                continue;
            }
            style.backgroundColor = incorrect;

            // -----
            if (!check[id]) {
                style.backgroundColor = bydefault;
                continue;
            }

            // -----
            if (check[id](value)) {
                style.backgroundColor = correct;
            }

        }

    }


    //     ----------------
    //  4. Initialize page.
    //     ----------------
    privates.initialize = function() {
        $("#output").prop({
            disabled: true
        }).addClass("no-cursor");
    };


    //     -------------
    //  5. Refresh page.
    //     -------------
    privates.refresh = function() {
        $("#refresh").on("click", function() {
            var $postdata = $.get("/audiocollection/refreshrippedcd");
            $postdata.done(function() {
                $(location).attr("href", "/audiocollection/rippedcdlogs?page=" + $("#container").find("#pages").children("b").text());
            });
        });
    };


    //     -----------
    //  6. Create log.
    //     -----------
    privates.create = function() {
        $("#create").on("click", function() {
            var $postdata = $.get(url.create);
            $postdata.done(function(response) {

                // -----
                $("#div3").wrapInner(response.dialog);
                var boxW = parseFloat($("#audiotags").css("width"));
                $("#audiotags").css({
                    left: winW / 2 - boxW / 2
                });

                // -----
                var $submit = $("#audiotags-form").find(":submit");
                if ($submit.length) {
                    $submit.attr({
                        value: "Create"
                    });
                }

            });
        });
    };


    //     --------------------
    //  7. Control page events.
    //     --------------------
    privates.pagecontroler = function() {

        //  7.a. Enable both "submit" and "reset" button once a radio button is checked.
        $("#rippedcd-form").find("div").children(":radio").on("change", function() {
            $("#rippedcd-form").children(".button").prop({
                disabled: false
            }).removeClass("no-cursor");
        });

        //  7.b. Disable both "submit" and "reset" button once "reset" is pressed.
        $("#rippedcd-form").children(":reset").on("click", function() {
            $("#rippedcd-form").children(".button").prop({
                disabled: true
            }).addClass("no-cursor");
        });

        //  7.c. Control submit event.
        $("#rippedcd-form").submit(function(event) {

            // Prevent default behavior.
            event.preventDefault();

            // Store selected row ID.
            var $rowid = $(this).data("rowid", $(this).find("input:checked").attr("value"));

            // Get respective log.
            var $postdata = $.post(url.update, "mode=update&" + $(this).serialize());

            // Display respective log on success.
            $postdata.done(function(response) {

                // -----
                $(window).scrollTop(0);
                $("body").addClass("no-scroll");
                $("#div3").wrapInner(response.dialog);

                // -----
                var boxW = parseFloat($("#audiotags").css("width"));
                $("#audiotags").css({
                    left: winW / 2 - boxW / 2
                });
                $before = $("#audiotags-form").serialize();

                // -----
                inittagsstyle(document.querySelector("#action").value);

            });

        });

    };


    //     --------------------
    //  8. Control form events.
    //     --------------------
    privates.formcontroler = function() {

        $("#div3")


        //  8.a. Enable  both "submit" and "reset" buttons once delete action is chosen.
        //       Disable both "submit" and "reset" buttons once update action is chosen.
        .on("change", "#action", function() {

            var $reset = $("#audiotags-form").find(":reset"),
                $submit = $("#audiotags-form").find(":submit"),
                $cancel = document.getElementById("cancel");

            switch ($(this).val().toLowerCase()) {


                //  8.a.i.   Delete.
                case "delete":

                    // Remove "reset" button.
                    if ($reset.length) {
                        $reset.remove();
                    }

                    // Rename "submit" button.
                    if ($submit.length) {
                        $submit.removeClass("no-cursor").prop({
                            disabled: false
                        }).attr({
                            value: "Delete"
                        });
                    }

                    // Disable both input fields and "#genre".
                    $("#audiotags-form").find("input").each(function() {
                        if ($(this).prop("required")) {
                            $(this).prop({
                                disabled: true,
                                required: false
                            });
                        }
                    });
                    $("#genre").prop({
                        disabled: true
                    });
                    break;


                    //  8.a.ii.  Update.
                case "update":

                    // Create "reset" button.
                    if (!$reset.length) {
                        var input = document.createElement("input");
                        input.type = "reset";
                        input.value = "Reset";
                        input.disabled = true;
                        input.classList.add("button");
                        input.classList.add("no-cursor");
                        $cancel.parentNode.insertBefore(input, $cancel);
                    }

                    // Rename "submit" button.
                    if ($submit.length) {
                        $submit.addClass("no-cursor").prop({
                            disabled: true
                        }).attr({
                            value: "Update"
                        });
                    }

                    // Enable both input fields and "#genre".
                    $("#audiotags-form").find(":text, input[type='number']").prop({
                        disabled: false,
                        required: true
                    });
                    $("#genre").prop({
                        disabled: false
                    });
                    break;


            }

            inittagsstyle(document.querySelector("#action").value);
        })


        //  8.b. Enable both "submit" and "reset" buttons once an input field is changed.
        .on("keyup change", "#set2", function() {
            $(this).closest("form").find(":submit, :reset").removeClass("no-cursor").prop("disabled", false);
        })

        //  8.c. Control input text fields content.
        .on("focusin focusout keyup", "input[type='text']", function() {
            var id = $(this).attr("id").toLowerCase(),
                value = $(this).val();
            $(this).css("backgroundColor", incorrect);
            if (check[id](value)) {
                $(this).css("backgroundColor", correct);
            }
        })

        //  8.d. Control "#year" content.
        .on("focusin focusout keyup change", "#year", function() {
            var id = $(this).attr("id").toLowerCase(),
                value = $(this).val();
            $(this).css("backgroundColor", incorrect);
            if (check[id](value)) {
                $(this).css("backgroundColor", correct);
            }
        })

        //  8.e. Change background color when select fields get focus.
        .on("focusin focusout", "select", function(ev) {
            switch (ev.type) {
                case "focusin":
                    $(this).css("backgroundColor", focused);
                    break;
                case "focusout":
                    $(this).css("backgroundColor", bydefault);
                    break;
            }
        })

        //  8.f. Change background color when "#ripped" gets focus.
        .on("focusin focusout", "#ripped", function(ev) {
            switch (ev.type) {
                case "focusin":
                    $(this).css("backgroundColor", focused);
                    break;
                case "focusout":
                    $(this).css("backgroundColor", bydefault);
                    break;
            }
        })

        //  8.g. Disable both "submit" and "reset" buttons once "reset" button is pressed.
        .on("reset", "#audiotags-form", function() {
            $(this).find(":submit, :reset").addClass("no-cursor").prop("disabled", true);
            $("#audiotags-form").find(":text, input[type='number']").prop({
                disabled: false,
                required: true
            });
            $("#genre").prop({
                disabled: false
            });
        })


        //  8.h. Control submit event.
        .on("submit", "#audiotags-form", function(event) {
            var data,
                action,
                $postdata;

            //  8.h.i.   Prevent default behavior.
            event.preventDefault();

            //  6.h.ii.  Serialize submitted data.
            $after = $(this).serialize();

            //  8.h.iii. Store both action and submitted data.
            //           Append row ID to submitted data.
            action = "create";
            if ($("#action").length > 0) {
                action = $("#action").val();
            }
            $(this).data("action", action);
            $(this).data("data", $after + "&action=" + action);

            //  8.h.iv.  Check submitted data with python using POST method.
            switch (action.toLowerCase()) {

                // CREATE/UPDATE log.
                case "create":
                case "update":

                    if ($after !== $before) {
                        $postdata = $.post(url.check, $(this).data("data"));
                        $postdata.done(function(response) {
                            $(response.dialog).insertAfter("#container5");
                            var boxW = parseFloat($("#audiotags").css("width"));
                            $("#dialogbox").css({
                                top: 100,
                                left: winW / 2 - boxW / 2
                            });
                        });
                    }

                    if ($after === $before) {
                        data = "head=Update log&body=Any tag hasn't been changed. Can't update the selected log.&template=t06a";
                        $postdata = $.post(url.dialogbox, encodeURI(data));
                        $postdata.done(function(response) {
                            $(response.dialog).insertAfter("#container5");
                            var boxW = parseFloat($("#audiotags").css("width"));
                            $("#dialogbox").css({
                                top: 100,
                                left: winW / 2 - boxW / 2
                            });
                        });
                    }

                    break;

                    // DELETE log.
                case "delete":
                    data = "head=Delete log&body=Would you like to delete the selected log?&template=t06b";
                    $postdata = $.post(url.dialogbox, encodeURI(data));
                    $postdata.done(function(response) {
                        $(response.dialog).insertAfter("#container5");
                        var boxW = parseFloat($("#audiotags").css("width"));
                        $("#dialogbox").css({
                            top: 100,
                            left: winW / 2 - boxW / 2
                        });
                    });
                    break;

            }

        })


        //  8.i. Control cancel event.
        .on("click", "#cancel", function() {
            $(location).attr("href", "/audiocollection/rippedcdlogs?page=" + $("#container").find("#pages").children("b").text());
        });


    };


    //     --------------------------
    //  9. Control dialog box events.
    //     --------------------------
    privates.dialogboxcontroler = function() {

        $("#div3")


        //  1. Button "OK": go back to the form.
        .on("click", "#button_ok", function() {
            $("#dialogoverlay-2").remove();
            $("#dialogbox").remove();
        })


        //  2. Button "NO": go back to the form.
        .on("click", "#button_no", function() {
            $("#dialogoverlay-2").remove();
            $("#dialogbox").remove();
        })


        //  3. Button "YES": update respective log.
        .on("click", "#button_yes", function() {

            // Remove dialog box.
            $("#dialogoverlay-2").remove();
            $("#dialogbox").remove();

            // Update respective log with python using POST method.
            // Change button ID from "OK" to "OUT".
            var action = $("#audiotags-form").data("action");
            if (action === "update" || action === "delete") {
                $("#audiotags-form").data("data", $("#audiotags-form").data("data") + "&rowid=" + $("#rippedcd-form").data("rowid"));
            }
            var $postdata = $.post(url.store, $("#audiotags-form").data("data"));
            $postdata.done(function(response) {
                $(response.dialog).insertAfter("#container5");
                var boxW = parseFloat($("#audiotags").css("width"));
                $("#dialogbox").css({
                    top: 100,
                    left: winW / 2 - boxW / 2
                });
                $("#dialogboxfoot").children("button").attr("id", "button_out");
            });

        })


        //  4. Button "OUT": exit form.
        .on("click", "#button_out", function() {
            var $postdata = $.get("/audiocollection/refreshrippedcd");
            $postdata.done(function() {
                if ($("#audiotags-form").data("action") === "update") {
                    $(location).attr("href", "/audiocollection/rippedcdlogs?page=" + $("#container").find("#pages").children("b").text());
                } else {
                    $(location).attr("href", "/audiocollection/rippedcdlogs");
                }
            });
        });

    };


    //     ---------
    // 10. Edit log.
    //     ---------
    privates.edit = function() {

        $(":checkbox").on("click", function() {

            // 10.a. Enable "output" button once an edit mode is checked.
            if ($(":checkbox:checked").length > 0) {
                $("#output").prop({
                    disabled: false
                }).removeClass("no-cursor");
            }

            // 10.b. Disable "output" button if all edit modes are unchecked.
            if ($(":checkbox:checked").length === 0) {
                $("#output").prop({
                    disabled: true
                }).addClass("no-cursor");
            }

        });

        // 10.c. Post python request once "output" button is pressed.
        $("#output").on("click", function() {
            var $posting = $.post("/audiocollection/rippedcdlogsreport", $("#availableoutputs-form").serialize());
            $posting.done(function() {
                $("#output").prop({
                    disabled: true
                }).addClass("no-cursor");
                $(":checkbox:checked").prop({
                    checked: false
                });
            });
        });

    };


    //     ----------------
    // 11. Page controlers.
    //     ----------------
    publics.init = function() {
        privates.initialize();
        privates.refresh();
        privates.create();
        privates.edit();
        privates.pagecontroler();
        privates.formcontroler();
        privates.dialogboxcontroler();
    };


})(website.rippedcdlogs = {});