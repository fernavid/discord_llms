ALICE_TOKEN = 
BOB_TOKEN = 
OPENAI_API_KEY = 

import discord
import openai
import asyncio

# Set up the OpenAI API key
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True

alice = discord.Client(intents=intents)
bob = discord.Client(intents=intents)

async def generate_response(prompt):
    print('\t Generating response...')
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.7,
        max_tokens=500,
    )
    print('\t Response generated')
    return response.choices[0].message["content"].strip()


@alice.event
async def on_ready():
    print(f"Bot 1 logged in as {alice.user}")


@alice.event
async def on_message(message):
    if message.author == alice.user:
        return

    if "Good job!" in message.content and message.author == bob.user:
        return

    if message.channel.name == "general":
        if message.author == bob.user:
            print("Alice got message from bob")
            prompt = f'''
            An AI Model has reviewed your answer and has these critiques. Review them and improve your answer.
            If the criticism is wrong or doesn't suggest improvement, respond with nothing but "NO IMPROVEMENT POSSIBLE"
            Always quote the exact original answer before working on the improvements (Original question: )        

            CRITIQUE:

            {message.content}

            Answer the question by providing the original question, feedback, and your revised answer in the following format:
            Original Question: ...
            Answer: ...
            '''
        else:
            print("Alice got message from user")
            prompt = f'''
            Respond, but include the exact question you are answering at the beginning of your response, using the following format:

            Original Question: {message.content}
            Answer: ...
            '''
        response = await generate_response(prompt)

        await message.channel.send(response)


@bob.event
async def on_ready():
    print(f"Bot 2 logged in as {bob.user}")


@bob.event
async def on_message(message):
    if message.author == bob.user or message.author != alice.user:
        return

    if "NO IMPROVEMENT POSSIBLE" in message.content and message.author == alice.user:
        await message.channel.send("Good job!")
        return

    if message.channel.name == "general":
        print("Bob got message from Alice")
        prompt = f'''
        Criticize the weak points this answer provided by a language model. 
        Absolutely NEVER! suggest an improved answer yourself, or offer an alternative answer.
        Always restate the exact original question before suggesting the improvements (ie. start your response with "Original question: ...").        

        ANSWER FROM LANGUAGE MODEL:
        {message.content}

        Provide your critique in the following format:
        Original Question: ...
        Feedback: ...
        '''
        critique_response = await generate_response(prompt)
        await message.channel.send(critique_response)


async def main():
    await asyncio.gather(
        alice.start(ALICE_TOKEN),
        bob.start(BOB_TOKEN)
    )

asyncio.run(main())
