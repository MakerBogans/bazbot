from bazbot.vectors import Vectinator

if __name__ == "__main__":
    vectinator = Vectinator()
    while True:
        query = input("Enter a message to search for: ")
        results = vectinator.search(query)
        if len(results) == 0:
            print("No results found.")
        else:
            for result in results:
                print(result)
