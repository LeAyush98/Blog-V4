def decor(function ) -> str:
    def wrap_boi(num):
        print("First came me")
        function(num)
    return wrap_boi

@decor
def test(num):
    if num > 3:
        print("then i came")



test(4)    