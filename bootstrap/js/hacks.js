$(document).ready(function()
{
    $.each(["change", "blur", "keydown", "keypress", "keyup", "paste"], function(i, ev)
    {
        $("body").on(ev, "input[type=text], input[type=password], textarea", function()
        {
            var val = $(this).val();
            
            var replacement_map = 
            {
                "ʼ": "'",
                "‘": "'",
                "`": "'",
                "’": "'",
                "ʼ": "'",
                "ʼ": "'",
                "ˮ": "\"",
                "ˮ": "\"",
                "ˮ": "\"",
                "“": "\"",
                "„": "\"",
                "”": "\"",
                "՚": "'",
                "՚": "'",
                "’": "'",
                "＇": "'",
                "À": "A",
                "À": "A",
                "Á": "A",
                "Á": "A",
                "Â": "A",
                "Â": "A",
                "Ã": "A",
                "Ã": "A",
                "Ä": "A",
                "Ä": "A",
                "Å": "A",
                "Å": "A",
                "Å": "A",
                "à": "a",
                "à": "a",
                "á": "a",
                "á": "a",
                "â": "a",
                "â": "a",
                "ã": "a",
                "ã": "a",
                "ä": "a",
                "ä": "a",
                "å": "a",
                "å": "a",
                "å": "a",
                "È": "E",
                "È": "E",
                "É": "E",
                "É": "E",
                "Ê": "E",
                "Ê": "E",
                "Ë": "E",
                "Ë": "E",
                "è": "e",
                "è": "e",
                "é": "e",
                "é": "e",
                "ê": "e",
                "ê": "e",
                "ë": "e",
                "ë": "e",
                "Ì": "I",
                "Ì": "I",
                "Í": "I",
                "Í": "I",
                "Î": "I",
                "Î": "I",
                "Ï": "I",
                "Ï": "I",
                "ì": "i",
                "ì": "i",
                "í": "i",
                "í": "i",
                "î": "i",
                "î": "i",
                "ï": "i",
                "ï": "i",
                "Ò": "O",
                "Ó": "O",
                "Ô": "O",
                "Õ": "O",
                "Ö": "O",
                "ò": "o",
                "ó": "o",
                "ó": "o",
                "ô": "o",
                "õ": "o",
                "ö": "o",
                "Ù": "U",
                "Ú": "U",
                "Û": "U",
                "Ü": "U",
                "ù": "u",
                "ú": "u",
                "û": "u",
                "ü": "u",
                "Ñ": "N",
                "ñ": "n",
                "—": "-",
                "\xa0": " "
            };

            $.each(Object.keys(replacement_map), function(ii, key)
            {
                while(val.indexOf(key) > -1)
                {
                    val = val.replace(key, replacement_map[key]);
                }
            });
            val = val.replace("\xa0", " ");
            $(this).val(val);
        });
    });
});