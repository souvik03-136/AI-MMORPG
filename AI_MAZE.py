import openai

openai.api_key = "api_key"

def generate_dnd_maze():
    text = "Develop a playable Dungeons and Dragons scenario where the player navigates a 20x40 ASCII dungeon maze using the W, A, S, D keys." \
           " Draw the maze with a designated start (S) and end (E) point. Integrate components like traps and challenges." \
           " Offer commands for gameplay and request descriptions for each new scenario. " \
           "Commence by illustrating the initial maze and setting the stage for an immersive adventure. My further commands will be in the form of w,a,s,d or W,A,S,D"
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": text}])
    return completion.choices[0].message.content

maze_result = generate_dnd_maze


def play(user_input):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": user_input}])
    return completion.choices[0].message.content
