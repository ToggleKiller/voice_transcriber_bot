import discord
from discord.ext import commands
import speech_recognition as sr
from pydub import AudioSegment
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Setup Bot with Command Prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Setup Recognizer
r = sr.Recognizer()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="transcribe")
async def transcribe(ctx, lang_code="fr-FR"):
    """
    Usage: Reply to a voice message with !transcribe
    Optional: !transcribe en-US (for English) or !transcribe fr-FR (for French)
    """
    
    # Check if the user replied to a message
    if not ctx.message.reference:
        await ctx.send("❌ You must **reply** to a voice message to use this command!")
        return

    # Get the message the user replied to
    replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    # Check for attachments in that message
    if not replied_message.attachments:
        await ctx.send("❌ That message has no audio attachment.")
        return

    attachment = replied_message.attachments[0]
    
    # Verify it is audio
    if not attachment.content_type.startswith('audio/'):
        await ctx.send("❌ That attachment doesn't look like audio.")
        return

    # Notify user
    status_msg = await ctx.send(f"🎧 Processing (Language: `{lang_code}`)...")

    #Start Processing 
    filename_ogg = f"voice_{replied_message.id}.ogg"
    filename_wav = f"voice_{replied_message.id}.wav"

    try:
        #Download
        await attachment.save(filename_ogg)

        #Convert (FFmpeg required)
        sound = AudioSegment.from_ogg(filename_ogg)
        sound.export(filename_wav, format="wav")

        #Transcribe
        with sr.AudioFile(filename_wav) as source:
            audio_data = r.record(source)
            # Use the 'lang_code' variable here (e.g., 'fr-FR' or 'en-US')
            text = r.recognize_google(audio_data, language=lang_code)
            
            await status_msg.edit(content=f"**Transcription:**\n{text}")

    except sr.UnknownValueError:
        await status_msg.edit(content="❌ Could not understand the audio.")
    except Exception as e:
        await status_msg.edit(content=f"❌ Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(filename_ogg): os.remove(filename_ogg)
        if os.path.exists(filename_wav): os.remove(filename_wav)

bot.run('TOKEN')