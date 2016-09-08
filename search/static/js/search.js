$(document).ready(function() {
    $('.report').click(function (e) {
        var $a = $(e.target);
        BootstrapDialog.show({
            type: BootstrapDialog.TYPE_WARNING,
            title: 'Warning',
            message: 'Not implemented.'
            });
    });

    $('.snapshot').click(function (e) {
        var $a = $(e.target);
        $.ajax($a.attr('data-json-url')).done(function (obj) {
            // alert(obj.content);
            BootstrapDialog.show({
                title: obj.title,
                message: obj.content.replace(highlight_re, function (m) {
                        return '<span class="keyword">' + m + '</span>';
                    })
            });
        });
    });
});
