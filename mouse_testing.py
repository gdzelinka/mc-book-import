from pynput.mouse import Controller

if __name__ == "__main__":
    mouse = Controller()
    print(mouse.position)