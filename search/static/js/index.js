$(document).ready(function() {
    var WdState=true;
    var BgState=true;
    var currbg=0;
    var useCustombox=true;
    $.ajaxSetup({cache:false});
    useCustombox=false;
    useCustombox=window.location.hash.indexOf('#showbox')>-1;
    if(window.navigator.userAgent.indexOf('Mobile')>-1) {
        useCustombox=false;
    }
    
    function proc_result(res) {
        //console.log(res);
        switch(res.action) {
            case "showdialog":
                showDialog(res.text);
                break;
            case "relocate":
                goTo(res.location);
                break;
            case "showcontent":
                showContent(res.text);
                break;
            default:
                break;
        } 
    }
    
    function ajax(url, data) {
        $.ajax({
            url: url,
            type: "POST",
            data: data,
            success: function(res) {
                proc_result($.parseJSON(res));
            }
        });
    }
    
    function reverse(s) {
        return s.split("").reverse().join("");
    }
    
    function changeWd() {
        var speed=500;
        if(WdState) {
            $("#Wd1").stop().fadeTo(speed,0);
            $("#Wd2").stop().delay(speed).fadeTo(speed,1);
        } else {
            $("#Wd2").stop().fadeTo(speed,0);
            $("#Wd1").stop().delay(speed).fadeTo(speed,1);
        }
        WdState=!WdState;
    }
    
    function changeBg() {
        var speed=500;
        var bg=["bg1.jpg", "bg2.jpg", "bg3.jpg", "bg4.jpg", "bg5.jpg"];
        ++currbg;
        if(currbg>=bg.length) {
            currbg=0;
        }
        var bgurl=bg[currbg];
        //bgurl=bg[Math.floor(Math.random()*bg.length)]; 
        //console.log(bgurl);
        if(BgState) {
            $("#bgbuffer2").css("background","url(/img/"+bgurl+")  no-repeat");
            $("#bgbuffer2").css("background-size","100% auto");
            $("#bgbuffer1").stop().fadeTo(speed,0);
            $("#bgbuffer2").stop().delay(speed).fadeTo(speed,1);
        } else {
            $("#bgbuffer1").css("background","url(/img/"+bgurl+")  no-repeat");
            $("#bgbuffer1").css("background-size","100% auto");
            $("#bgbuffer2").stop().fadeTo(speed,0);
            $("#bgbuffer1").stop().delay(speed).fadeTo(speed,1);
        }
        BgState=!BgState;
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
    
    function showDialog(str)
    {
        $("#dialog").find('.content').empty().append(str);
        $("#dialog").addClass("show");
        $("#dialogContainer").fadeTo(200,1);
    }
    
    function goTo(url) {
        window.location=url;
        //$("#main").fadeTo(200,0);
        //setTimeout(function() {window.location=url;},200);
    }
    
    function showContent(content) {
        $("#main").fadeTo(200,0);
        setTimeout(function() {$("#main").html(content).fadeTo(200,1);},200); 
    }
    
    function showStatus(cmd) {
        showDialog("<div class=\"loading statusbox\"></div>");
        $.ajax({
            url: "ajax.php?action=status",
            type: "POST",
            data: {"command":cmd},
            success: function(res) {
                //$("#dialogContainer").fadeTo(200,0);
                /*setTimeout(function() {*/showDialog("<div class=\"statusbox\">"+res+"</div>");/*},200);*/
            }
        });
    }
    
    function showTxtLoading() {
        $("#txt").addClass("loading");
    }
    
    function hideTxtLoading() {
        $("#txt").removeClass("loading");
    }
    
    //setGradual($("#box"));    
    setGradual($("#btn1"),0.7);
    setGradual($("#btn2"),0.7);
    setGradual($("#btnOK"),0.7);
    setGradual($("#blog"),0.5);
    setGradual($("#lab"),0.5);
    setGradual($("#status"),0.5);
    
    _onSearch=(function() {
        var $txt=$("#txt");
        if($txt.val()=="") {
            $txt.val($txt.attr("placeholder"));
        }
        showTxtLoading();
        $txt.closest('form').submit();
        //ajax("ajax.php?action=search",{"keyword":$txt.val()});
    });
    $("#btn1").click(_onSearch);
    $("#txt").keydown(function(event) {if(event.keyCode == 13) _onSearch();});
    
    $("#btn2").click(function() {
        var $txt=$("#txt");
        if($txt.val()=="") {
            $txt.val($txt.attr("placeholder"));
        }
        showTxtLoading();
        ajax("ajax.php?action=lucky",{"keyword":$txt.val()});
    });
    
    $("#btnOK").click(function() {
        $("#dialogContainer").fadeOut(200);
    });    
    
    setInterval(function() {changeWd();},10000); //10秒后自动更新万呆图像
    //setInterval(function() {changeBg();},30000); //30秒自动更新背景图像
    
    $("#blog").html("Wandai Blog").click(function() {
        goTo("//twd2.me/");
    });
    $("#lab").html("Wandai Laboratory").click(function() {
        goTo("//lab.twd2.net/");
    });
    $("#egg").click(function () {
        showDialog("您好! 感谢您对万呆的支持! 祝您围观愉快!");
    });
    $("#main").fadeTo(200,1);
    $("#txt").focus();
});
