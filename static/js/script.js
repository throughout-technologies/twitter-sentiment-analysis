$.validator.addMethod("name_regx", function (value, element) {
    return this.optional(element) || (/^(#)?(@)?($)?[a-zA-Z0-9_-]*$/i.test(value) );
}, "Please enter a valid keyword.");

$.validator.addMethod("number_regx", function (value, element) {
    return this.optional(element) || (/^[1-9]\d*(\.\+)?$/i.test(value) );
}, "Please enter number greater than 0 without decimal.");

 

var v = jQuery("#mainform").validate({
    rules: {
        
        title: {
            required: true,
            minlength: 3,
            maxlength:120,
            name_regx: true,
           
        },
        record: {
            required: true,
            minlength: 1,
            number_regx:true,
        },

    },

    messages: {},
    errorElement: "span"

});

//   submit button

$("#submit").click(function () {
    if (v.form()) {
        $('#spinner').css('display',"block")
    }
});



