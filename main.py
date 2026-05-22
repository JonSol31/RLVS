from env.vex_env import VexEnv


def main():
    env = VexEnv()

    print("Environment initialized")

    state = env.reset()
    print(state)


if __name__ == "__main__":
    main()