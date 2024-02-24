import time
import progressbar

def print_sample_text_in_colors_25():
    colors = {
        "Black": "\033[30m",
        "Red": "\033[31m",
        "Green": "\033[32m",
        "Yellow": "\033[33m",
        "Blue": "\033[34m",
        "Magenta": "\033[35m",
        "Cyan": "\033[36m",
        "White": "\033[37m",
        "Bright Black": "\033[90m",
        "Bright Red": "\033[91m",
        "Bright Green": "\033[92m",
        "Bright Yellow": "\033[93m",
        "Bright Blue": "\033[94m",
        "Bright Magenta": "\033[95m",
        "Bright Cyan": "\033[96m",
        "Background Black": "\033[40m",
        "Background Red": "\033[41m",
        "Background Green": "\033[42m",
        "Background Yellow": "\033[43m",
        "Background Blue": "\033[44m",
        "Background Magenta": "\033[45m",
        "Background Cyan": "\033[46m",
        "Background White": "\033[47m",
        "Reset": "\033[0m"
    }

    sample_text = "Sample Text"

    for color_name, color_code in colors.items():
        colored_text = f"{color_code}{sample_text}{colors['Reset']}"
        print(f"{color_name}: {colored_text}")

def console_countdown(seconds):
    widgets = [
        'Countdown: ', 
        progressbar.Percentage(), ' ',
        progressbar.Bar(), ' ',
        progressbar.SimpleProgress(), ' ',
        progressbar.ETA()
    ]

    progress = progressbar.ProgressBar(maxval=seconds, widgets=widgets).start()

    for remaining_time in range(seconds, 0, -1):
        time.sleep(1)
        progress.update(seconds - remaining_time)

    progress.finish()
    print("Countdown complete!")

# Example usage
print_sample_text_in_colors_25()

# Example usage
countdown_seconds = 10
console_countdown(countdown_seconds)
