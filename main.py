from client import *
import os
from dotenv import load_dotenv
from chess_functions import DiscordChessGame, ChessPlayer, piece_aliases
import time

import speech_recognition as sr
from pydub import AudioSegment
import io

def main():
    # load environment variables from .env
    load_dotenv()

    client = VocalChessClient()
    vc_connections = {}

    @client.command()
    async def move_help(interaction: discord.Interaction):
        """Give the user information on how to move"""
        embed = discord.Embed()
        embed.set_author(name="How to Move with VocalChess")
        embed.add_field(name="Algebraic Chess Notation", value=
                        """You may use [Standard Algebraic Noation](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)) to make moves. An example of this is Nf3 to move a Knight to F3. To capture, you simple place an 'x' after the piece letter. For check, you must put + after the move, and checkmate must have # after the move. Short (king-side) castle is denoted by O-O and long (queen-side) castle is denoted by O-O-O. You may not have any spaces in the algebraic chess notation. Promotion, for example, would be e8=Q, e8=N, e8=B, or e8=R"""
                        , inline=False)
        embed.add_field(name="Universal Chess Interface", value=
                        """If you do not use Standard Algebraic Notation, the bot will check for [Universal Chess Interface](https://en.wikipedia.org/wiki/Universal_Chess_Interface) to make moves. An example of this is g1f3 to move the Knight from g1 to f3. You simply put the starting square followed by the end square. For promotion, simply put 'q', 'n', 'b', or 'r' after the four character notation. Again, no spaces are allowed."""
                        , inline=False)
        embed.add_field(name="Verbose Chess Moves", value=
                        """This bot is programmed to handle a variety of move cases that are not covered by Algebraic Notation or UCI, such as 'Knight to f3', 'En passant', 'Queen side castle', 'Long castles' 'Rook H to f5', et cetera. Unless you are castling or performing en passant, the first word (before space, hyphen, or underscore) **must** be a piece name, which can be followed by a file name if there are multiple legal moves with multiple given pieces (eg. two rooks moving on the same rank, would be 'Rook H to h5'). The last word **must** be the square on which to move, excepting the same circumstances of castling and en passant. For promotion, simply say the word 'promote' or 'promotes' and piece you wish to promote to in the bounds of the first and last word; if you do not specify, it will automatically promote to Queen. Multiple promotion cases that will work are 'e promotes e8', 'e promotes to queen on e8', 'e promotes to knight on e8', 'e promotes knight e8', et cetera."""
                        , inline=False)
        embed.add_field(name="Vocal Chess Moves", value=
                        """If using the vocal chess features of this bot, it will run through the same checks as if you sent a text message, first checking Algebraic Notation, followed by UCI, followed by the Verbose Chess Moves."""
                        , inline=False)

        await interaction.response.send_message(embed = embed, ephemeral=True)

    @client.command()
    async def player_stats(interaction: discord.Interaction, user: discord.Option(discord.User) = None):
        """Give player statistics"""
        if not user:
            user = interaction.user

        player = ChessPlayer(user)

        embed = discord.Embed()
        embed.set_author(name=f"VocalChess Statistics - {user.display_name}")
        embed.add_field(name="Elo Rating", value=f"{player.elo}", inline=True)
        embed.add_field(name="Wins / Losses / Draws", value=f"{player.wins} / {player.loss} / {player.draw}", inline=True)

        await interaction.response.send_message(embed = embed)

    @discord.guild_only()
    @client.command()
    async def setting(interaction: discord.Interaction, setting: discord.Option(str, choices=GuildInfo().__dict__.keys(), description="The thing you want to change"), value: discord.Option()):
        """Set a guild configuration setting"""
        client.set_guild_setting(interaction.guild_id, setting = setting, value = value)
        await interaction.response.send_message(f"Set {setting} to {value}!", ephemeral=True, delete_after=5)

    @discord.guild_only()
    @client.command()
    async def server_settings(interaction: discord.Interaction):
        """Display the guild configuration"""
    
        guild_data: GuildInfo = client.guild_data[interaction.guild_id] if client.guild_data.get(interaction.guild_id) else GuildInfo()

        embed = discord.Embed()
        embed.set_author(name=f"{interaction.guild.name} - VocalChess Configuration")
        for field in guild_data.__dict__.keys():
            embed.add_field(name = field, value = guild_data.__getattribute__(field))

        await interaction.response.send_message(embed = embed, ephemeral=True)

    @client.command()
    async def clear_dms(interaction: discord.Interaction):
        """Clears the bot DM's; primarily made for OCD debug purposes."""
        channel = await interaction.user.create_dm()
        messages = await channel.history().flatten()
        for message in messages:
            if message.author.bot:
                await message.delete()
        
        await interaction.response.send_message("Cleared your DMs with the bot!", ephemeral=True, delete_after=5)


    @client.command()
    async def challenge_cpu(interaction: discord.Interaction, color: discord.Option(str, choices=['white', 'black']) = 'white', elo: discord.Option(int) = 1500):
        """Challenge the CPU to a chess game."""

        # create appropriate ChessPlayer objects
        if color == 'white':
            white_player = ChessPlayer(interaction.user)
            black_player = ChessPlayer(client.user, elo, bot=True)
        else:
            white_player = ChessPlayer(client.user, elo, bot=True)
            black_player = ChessPlayer(interaction.user)

        channel = await client.create_dm(interaction.user)
        # create chess game instance
        game = DiscordChessGame(channel = channel.id, white = white_player, black = black_player)

        # CPU makes first move if player is black
        if color == 'black':
            client.engine.set_elo_rating(elo)
            # reset board
            client.engine.set_position(None)
            move = client.engine.get_best_move()
            game.game.push_uci(move)

        e = game.get_embed()

        # add this game to the games so it can be tracked by the discord bot
        client.games.append(game)
        view = CPUGameView()
        view.game = game
        view.engine = client.engine
        ctx = await channel.send(file = e['file'], embed = e['embed'], view=view)
        game.ctx = ctx

        await interaction.response.send_message(content = f"A chess game has started in your DMs with this bot!", delete_after = 30, ephemeral = True)

    @discord.guild_only()
    @client.command()
    async def challenge(interaction: discord.Interaction, opponent: discord.Option(discord.User), color: discord.Option(str, choices=['white', 'black']) = 'white', public: discord.Option(bool) = True):
        """Challenge another user to a chess game."""
        
        channel = await client.create_dm(opponent)
        view = GameOfferView()
        view.client = client
        view.interaction = interaction
        view.opponent = opponent
        view.color = color
        view.public = public
        await channel.send(f"{interaction.user.name} has challenged you to a game of chess in {interaction.guild.name}!", view=view)
        await interaction.response.send_message(f"You have challenged {opponent.name} to a chess game - they have recieved a DM to accept or decline your request. If they accept, a channel will be created in this server.", ephemeral=True, delete_after=10)

    @tasks.loop(seconds = 1)
    async def check_voice(interaction: discord.Interaction, game: DiscordChessGame):
        """
        Check if Bot detected user voice and give user 
         x more seconds to talk and then cancels it to 
         run the callback function "voiceReceiver_callback"
        """
        
        vc = get(client.voice_clients, guild=interaction.guild)
        if not vc.recording:
            sink = discord.sinks.MP3Sink(filters={'time': 0})
            # client.sink = sink
            client.timer = time.time()
            # print("started recording") 
            vc.start_recording(sink, process_voice, game)

        # if we're recording, check that 5 seconds have past and target user is not currently talking
        if vc.recording and (time.time()-client.timer >= 5):
            # print("stopped recording")
            vc.stop_recording()
            client.waiting = False     

    # speech recognition object
    r = sr.Recognizer()
    def speech_to_text(audio_bytes: io.BytesIO | str):
        """Convert speech to text using google speech recognition. Gives multiple possibilities."""

        # discord passes oddly formatted, we need to resave it
        sound_conversion = AudioSegment.from_file(audio_bytes)

        converted_audio = io.BytesIO()
        sound_conversion.export(converted_audio, format='wav')

        text = ""
        with sr.AudioFile(converted_audio) as source:
            try:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened, language = 'en-US', show_all=True)

                except sr.UnknownValueError as e:
                    text = "*inaudible*"
                except Exception as e: 
                    print(e)
            except:
                text = ""

        return text

    async def process_voice(sink: discord.sinks.MP3Sink, game: DiscordChessGame, *args):
        """Process voice after recording is stopped"""    
        audio_data: io.BytesIO = None

        for user_id, audio in sink.audio_data.items():
            # if it's the user we're trying to listen to, set their audiodata to the thingy
            if user_id == (game.white.user.id if game.game.turn else game.black.user.id):
                audio_data = audio.file

        if not audio_data: return

        # get possibilities from speech_to_text
        speech_rec = speech_to_text(audio_data)

        # pass the list of possibilities to try_speechrec_move
        game.try_speechrec_move(speech_rec)
        
    async def join(interaction: discord.Interaction, game: DiscordChessGame):
        voice = interaction.user.voice

        if not voice:
            await interaction.response.send_message("You aren't in a voice channel!", ephemeral=True)
            return

        vc = await voice.channel.connect()
        vc_connections.update({interaction.guild.id: vc})
        check_voice.start(interaction, game)

    @discord.guild_only()
    @client.command()
    async def leave(interaction: discord.Interaction):
        if interaction.guild.id in vc_connections:  # Check if the guild is in the cache.
            vc = vc_connections[interaction.guild.id]
            await vc.disconnect()
            del vc_connections[interaction.guild.id]  # Remove the guild from the cache.
            check_voice.stop()
        else:
            await interaction.response.send_message("I am currently not in a channel.", ephemeral=True)  # Respond with this if we aren't recording.

    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()