from .scheme import evaluate

def repl():
    env = {}
    try:
        while True:
            expr = input(">> ")
            try:
                result = evaluate(expr, env)
                print(result)
            except (SyntaxError, ValueError) as e:
                print(e) 
                continue
            
    except EOFError:
        print("Bye!")
        exit()

if __name__ == "__main__":
    repl()