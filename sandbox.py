def f():
    try:
        return 42
    except:
        return 0
    finally:
        print("Nettoyage")

f()