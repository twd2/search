$(document).ready(function() {
    var WdState = true;
    var BgState = true;
    var currbg = 0;
    $.ajaxSetup({ cache: false });
    
    function reverse(s) {
        return s.split("").reverse().join("");
    }
    
    function changeWd() {
        var speed=500;
        if(WdState) {
            $("#Wd1").stop().fadeTo(speed, 0);
            $("#Wd2").stop().delay(speed).fadeTo(speed, 1);
        } else {
            $("#Wd2").stop().fadeTo(speed, 0);
            $("#Wd1").stop().delay(speed).fadeTo(speed, 1);
        }
        WdState = !WdState;
    }
    
    function changeBg() {
        var speed = 500;
        var bg = ["bg1.jpg", "bg2.jpg", "bg3.jpg", "bg4.jpg", "bg5.jpg"];
        ++currbg;
        if (currbg >= bg.length) {
            currbg = 0;
        }
        var bgurl = bg[currbg];
        //bgurl=bg[Math.floor(Math.random()*bg.length)]; 
        //console.log(bgurl);
        if (BgState) {
            $("#bgbuffer2").css("background","url(/img/" + bgurl + ")  no-repeat");
            $("#bgbuffer2").css("background-size", "100% auto");
            $("#bgbuffer1").stop().fadeTo(speed, 0);
            $("#bgbuffer2").stop().delay(speed).fadeTo(speed, 1);
        } else {
            $("#bgbuffer1").css("background","url(/img/" + bgurl + ")  no-repeat");
            $("#bgbuffer1").css("background-size", "100% auto");
            $("#bgbuffer2").stop().fadeTo(speed, 0);
            $("#bgbuffer1").stop().delay(speed).fadeTo(speed, 1);
        }
        BgState = !BgState;
    }
    
    function setGradual(obj, def) {
        obj.css("opacity", def); 
        obj.hover(
        function() { 
            obj.stop().fadeTo(200,1);
        }, 
        function() { 
            obj.stop().fadeTo(200,def);
        });
    }
    
    function showTxtLoading() {
        $("#txt").addClass("loading");
    }
    
    function hideTxtLoading() {
        $("#txt").removeClass("loading");
    }

    setGradual($("#btn1"),0.7);
    setGradual($("#btn2"),0.7);
    
    _onSearch = (function() {
        var $txt = $("#txt");
        if ($txt.val() == "") {
            $txt.val($txt.attr("placeholder"));
        }
        showTxtLoading();
        $txt.closest('form').submit();
    });

    $("#btn1").click(_onSearch);
    $("#txt").keydown(function(event) { if (event.keyCode == 13) _onSearch(); });
    
    $("#btn2").click(function() {
        var $txt = $("#txt");
        if ($txt.val() == "") {
            $txt.val($txt.attr("placeholder"));
        }
        showTxtLoading();
        var $form = $txt.closest('form');
        $form.attr('action', '/advanced');
        $form.submit();
    });
    
    $("#btnOK").click(function() {
        $("#dialogContainer").fadeOut(200);
    });    
    
    setInterval(function() { changeWd(); }, 10000); //10秒后自动更新万呆图像
    //setInterval(function() { changeBg(); }, 30000); //30秒自动更新背景图像

    $("#egg").click(function () {
        BootstrapDialog.show({
            title: '您好',
            message: "您好! 感谢您对万呆的支持! 祝您围观愉快!"
        });
    });
    $("#main").fadeTo(200, 1);
    $("#txt").focus();
});
