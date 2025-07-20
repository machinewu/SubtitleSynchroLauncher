# Subtitle Synchro Launcher

[-->中文文档<--](./README_CN.md)

Subtitle Synchro Launcher is a universal GUI launcher designed for convenient subtitle synchronization. It allows users to add source video/audio, source subtitles, and destination video/audio files via simple drag-and-drop, then calls external subtitle synchronization tools to align subtitle timing. Basic pre- and post-processing of subtitles is also supported.

- Supports various command-line subtitle synchronization tools ([Sushi](https://github.com/FichteFoll/Sushi), [alass](https://github.com/kaegi/alass), [FFsubsync](https://github.com/smacke/ffsubsync), etc.), with customizable parameters.
- Supports concurrent processing of multiple tasks and allows stopping tasks during runtime.
- Supports adding files/folders via drag-and-drop.
- Allows reordering and sorting of file lists, including correct alphanumeric sorting for filenames with unaligned numbers (e.g., `a8.mkv, a9.mkv, a10.mkv, a11.mkv`).
- Customizable UI styles.
- Multi-language support.

![operation_en](https://github.com/user-attachments/assets/a6cadf68-cf7b-45b9-987b-c2c7636f053a)
![snapshot_en](https://github.com/user-attachments/assets/2ab438a8-0dd3-4a12-9187-17881ddbcc33)

### Usage

1. Add source video/audio, source subtitles, and destination video/audio files by **dragging and dropping** or clicking the "➕" button. Dragging and dropping can involve folders. Source video/audio and subtitles can be dragged in together and will be assigned to the corresponding listboxes automatically. The button only supports adding files, not folders.
2. If the output directory is left blank, it will be set automatically based on the destination video/audio input. You can modify it as needed.
3. Check whether the line numbers of the files in the listbox correspond correctly row by row. You can sort, delete, or filter as needed.
4. Click the "Run" button to start synchronization tasks. Progress and logs will be shown in the console.
5. To terminate a task during runtime, click the "Stop" button (visible only during execution).

#### Notes:

- Python 3.10+ is recommended. While Python 3.8+ is supported, some UI features may be missing in these lower versions (e.g., listbox background striping).
- Required Python modules: `aiofiles`, `charset_normalizer`, `tkinterdnd2`. You can install with `pip install -r requirements.txt` or `pip install aiofiles charset_normalizer tkinterdnd2`.
- You can specify a custom config file path as a parameter when launching Subtitle Synchro Launcher (on Windows, add it to the shortcut Target). If no parameter is given, placing `config.ini` in the program directory will load it automatically. If loaded successfully, the profile name will appear in the program title.
- By default, Sushi is configured for synchronization, requiring `ffmpeg`, `ffprobe`, and `sushi` to be available in your system PATH. If not, specify their paths in `config.ini`.
- Restart the program after modifying the config file for changes to take effect.
- With concurrency set to 1, logs are output in real time. With higher concurrency, logs for each command are output after completion to prevent interleaving.
- The output directory field automatically expands to an absolute path. Entering `.` means the program's startup directory.
- Most UI elements have tooltips; hover your mouse for more information.


## Configuration File Guide

**Note**: 
- The config file does not support direct line breaks. Use the tab character "	" (the Tab key \t, but \t cannot be written explicitly) to indicate a line break.
- The configuration file must be encoded in UTF-8.
- A line can be commented out by starting it with # or ; (inline comments are not supported).

### 1\. General Configuration [general]

|            Option            |                                                                                                                                   Description                                                                                                                                    |                                                   Default Value                                                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| subtitle_ext                 | Subtitle file extensions, used to filter input files into the subtitle listbox. Separate multiple extensions with commas.                                                                                                                                                        | `ass, srt, ssa`                                                                                                    |
| media_ext                    | Supported video/audio file extensions, used to filter input files into the video/audio listbox. Separate multiple extensions with commas.                                                                                                                                        | `mkv, mp4, m4a, avi, wmv, flv, rm, rmvb, mov, vob, mpeg, webm, mp3, wav, flac, ape, aac, ac3, opus, ogg, wma, amr` |
| launch_resolution            | Window resolution at startup, in the format `{width}x{height}`.                                                                                                                                                                                                                  | `1440x600`                                                                                                         |
| min_resolution               | Minimum window resolution, in the format `{width}x{height}`.                                                                                                                                                                                                                     | `860x360`                                                                                                          |
| tips_trigger_time_ms         | Tooltip trigger time for buttons (milliseconds). Integer.                                                                                                                                                                                                                        | `400`                                                                                                              |
| listbox_tips_trigger_time_ms | Tooltip trigger time for listbox cells (milliseconds). Integer.                                                                                                                                                                                                                  | `600`                                                                                                              |
| top_most                     | Whether to keep the window always on top at startup. `yes` or `no`.                                                                                                                                                                                                              | `yes`                                                                                                              |
| checkbox_listbox_repeatable  | Allow duplicate files in the listbox (default value for the UI checkbox). `yes` or `no`.                                                                                                                                                                                         | `yes`                                                                                                              |
| checkbox_input_file_sorted   | Whether to sort input files before adding to the listbox (default value for the UI checkbox). `yes` or `no`.                                                                                                                                                                     | `yes`                                                                                                              |
| default_output_dir           | Default value for the output directory field.                                                                                                                                                                                                                                    |                                                                                                                    |
| task_parallel_number         | Number of tasks to run in parallel. Integer.                                                                                                                                                                                                                                     | `3`                                                                                                                |
| task_stages                  | Sequence of stage codes for each task (not necessarily numbers, but avoid symbols). Multiple codes separated by commas. Each code corresponds to a `[stage_*]` section. If any stage fails (non-zero exit code), subsequent stages are skipped and the task is marked as failed. | `1, 2, 3, 4, 5, 6`                                                                                                 |

### 2\. Style Configuration [style]

Note: Due to OS compatibility issues, some style settings may not take effect.

|              Option               |                                                    Description                                                    |   Default Value   |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------- |
| fontname                          | Font for controls without a specific font setting                                                                 | `Microsoft YaHei` |
| label_fontsize                    | Font size for labels                                                                                              | `9`               |
| label_tips_fontsize               | Font size for tip labels                                                                                          | `9`               |
| label_outputdir_icon_fontsize     | Font size for output directory icon                                                                               | `10`              |
| label_filter_icon_fontsize        | Font size for filter icon                                                                                         | `10`              |
| listbox_fontsize                  | Font size for listboxes                                                                                           | `9`               |
| entry_fontsize                    | Font size for input fields                                                                                        | `10`              |
| console_fontname                  | Font for the log output box                                                                                       | `Microsoft YaHei` |
| console_fontsize                  | Font size for the log output box                                                                                  | `10`              |
| context_menu_fontname             | Font for context menus                                                                                            | `Microsoft YaHei` |
| context_menu_fontsize             | Font size for context menus                                                                                       | `10`              |
| button_emoji_fontname             | Font for icon-style buttons                                                                                       | `Microsoft YaHei` |
| button_emoji_fontsize             | Font size for icon-style buttons                                                                                  | `10`              |
| button_execute_fontsize           | Font size for the Run button                                                                                      | `12`              |
| button_fontsize                   | Font size for buttons                                                                                             | `10`              |
| button_top                        | Text for "Move to Top" button                                                                                     | `⤒⤒`               |
| button_up                         | Text for "Move Up" button                                                                                         | `↑`               |
| button_down                       | Text for "Move Down" button                                                                                       | `↓`               |
| button_bottom                     | Text for "Move to Bottom" button                                                                                  | `⤓⤓`               |
| button_sort                       | Text for "Sort" button                                                                                            | `⇅`               |
| button_add                        | Text for "Add File" button                                                                                        | `➕`              |
| button_delete                     | Text for "Remove Selected" button                                                                                 | `✖`               |
| button_clear                      | Text for "Clear All" button                                                                                       | `🗑`              |
| button_topmost                    | Text for "Always on Top" button                                                                                   | `📌`              |
| button_directory                  | Text for output directory button                                                                                  | `📁`              |
| button_filter                     | Text for filter button                                                                                            | `🔍`              |
| color_frame_bg                    | Background color for module frames                                                                                | `#f0f0f0`         |
| color_label_bg                    | Background color for label controls                                                                               | `#f0f0f0`         |
| color_label_border                | Border color for label controls                                                                                   | `#a0a0a0`         |
| color_progressbar                 | Color of the progress bar                                                                                         | `#4a86e8`         |
| color_progressbar_bg              | Background color of the progress bar                                                                              | `#f0f0f0`         |
| color_progressbar_trough          | Track color of the progress bar                                                                                   | `#e6e6e6`         |
| color_checkbox_bg                 | Background color for checkboxes                                                                                   | `#f0f0f0`         |
| color_button_font                 | Font color for buttons                                                                                            | `#333333`         |
| color_button_font_active          | Font color for buttons when active                                                                                | `#0078d7`         |
| color_button_topmost_font         | Font color for "Always on Top" button                                                                             | `#ff2222`         |
| color_button_topmost_font_active  | Font color for "Always on Top" button when active                                                                 | `#ff8888`         |
| color_button_execute_font         | Font color for the Run button                                                                                     | `#18a24b`         |
| color_button_stop_font            | Font color for the Stop button                                                                                    | `#ff2222`         |
| color_listbox_font                | Font color for listboxes                                                                                          | `#000000`         |
| color_listbox_bg                  | Background color for listboxes                                                                                    | `#ffffff`         |
| color_odd_row_bg                  | Background color for odd rows in listboxes                                                                        | `#f5e6ff`         |
| color_even_row_bg                 | Background color for even rows in listboxes                                                                       | `#ffffff`         |
| color_console_font                | Font color for the log output box                                                                                 | `#000000`         |
| color_console_error_font          | Font color for error messages in the log output                                                                   | `#ff0000`         |
| color_console_system_font         | Font color for system messages in the log output                                                                  | `#0000ff`         |
| color_console_bg                  | Background color for the log output box                                                                           | `#ffffff`         |
| color_output_dir_entry_font       | Font color for the output directory field                                                                         | `#000000`         |
| color_output_dir_entry_bg         | Background color for the output directory field                                                                   | `#ffffff`         |
| color_output_dir_entry_height_fix | Height adjustment for the output directory field (used when the font is not fully displayed at the top or bottom) | `0`               |
| color_filter_entry_font           | Font color for the filter field                                                                                   | `#000000`         |
| color_filter_entry_bg             | Background color for the filter field                                                                             | `#ffffff`         |
| color_filter_entry_height_fix     | Height adjustment for the filter field (used when the font is not fully displayed at the top or bottom)           | `0`               |
| color_tips_font                   | Font color for tooltips                                                                                           | `#000000`         |
| color_tips_bg                     | Background color for tooltips                                                                                     | `#ffffe0`         |

### 3\. Internationalization [i18n]

The program includes built-in i18n configurations for English and Simplified Chinese. To add other languages, simply translate the corresponding entries.

### 4\. Variable Configuration [variable]

*Before each task runs*, variables in the form *`{XXX}` are replaced line by line*. If a variable is not found, an error will occur. Variables defined in subsequent lines can use variables defined in previous lines.

Some variables are reserved and cannot be overwritten, especially those ending with `_exe`. Other variables can be updated by the output of each stage, and subsequent stages will use the updated values.

**Note**: Variables ending with `_exe` (e.g., `XXX_exe`) will **NOT be replaced** (i.e., if its value contains `{YYY}`, `{YYY}` will not be replaced with the corresponding value). If its value is a path, the *directory where the path is located* will be added to the front of the `PATH` environment variable during task execution.

|       Option        |                                                                                                                         Description                                                                                                                         |                                        Default Value                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| output_dir          | Reserved. Output directory.                                                                                                                                                                                                                                 | Value from the output directory field                                                       |
| task_id             | Reserved. Task ID (row number in the file list).                                                                                                                                                                                                            | Task ID (row number in the file listbox)                                                    |
| temp_dir            | Reserved. Temporary directory. If set, it will be created before the task and deleted after completion.                                                                                                                                                     | {output_dir}_tmp{current time yyMMddHHmmss}-{task_id}                                       |
| src_media           | Reserved. Absolute path of the source video/audio for this task.                                                                                                                                                                                            | Absolute path of the source video/audio                                                     |
| src_media_name      | Reserved. Filename of the source video/audio (without extension).                                                                                                                                                                                           | Filename of the source video/audio (without extension)                                      |
| src_media_suffix    | Reserved. Extension of the source video/audio (without dot).                                                                                                                                                                                                | Extension of the source video/audio (without dot)                                           |
| src_media_dir       | Reserved. Absolute directory of the source video/audio (no trailing slash except for drive/root directory).                                                                                                                                                 | Absolute directory of the source video/audio (no trailing slash except for root/drive)      |
| src_subtitle        | Reserved. Absolute path of the source subtitle.                                                                                                                                                                                                             | Absolute path of the source subtitle                                                        |
| src_subtitle_name   | Reserved. Filename of the source subtitle (without extension).                                                                                                                                                                                              | Filename of the source subtitle (without extension)                                         |
| src_subtitle_suffix | Reserved. Extension of the source subtitle (without dot).                                                                                                                                                                                                   | Extension of the source subtitle (without dot)                                              |
| src_subtitle_dir    | Reserved. Absolute directory of the source subtitle (no trailing slash except for drive/root directory).                                                                                                                                                    | Absolute directory of the source subtitle (no trailing slash except for root/drive)         |
| dst_media           | Reserved. Absolute path of the destination video/audio.                                                                                                                                                                                                     | Absolute path of the destination video/audio                                                |
| dst_media_name      | Reserved. Filename of the destination video/audio (without extension).                                                                                                                                                                                      | Filename of the destination video/audio (without extension)                                 |
| dst_media_suffix    | Reserved. Extension of the destination video/audio (without dot).                                                                                                                                                                                           | Extension of the destination video/audio (without dot)                                      |
| dst_media_dir       | Reserved. Absolute directory of the destination video/audio (no trailing slash except for drive/root directory).                                                                                                                                            | Absolute directory of the destination video/audio (no trailing slash except for root/drive) |
| ffmpeg_exe          | Path to the FFmpeg executable. For it ends with `_exe`, variables in the value will not be replaced.                                                                                                                                                        | ffmpeg                                                                                      |
| ffprobe_exe         | Path to the FFprobe executable. For it ends with `_exe`, variables in the value will not be replaced. Required for the built-in procedures `get_audio_stream_idx`, `shift_source_subtitle_timeline_delay`, and `shift_destination_subtitle_timeline_delay`. | ffprobe                                                                                     |
| sushi_exe           | Path to the Sushi executable. For it ends with `_exe`, variables in the value will not be replaced.                                                                                                                                                         | sushi                                                                                       |
| Other variables     | Can be freely defined and modified by stage outputs.                                                                                                                                                                                                        | Customize as needed, e.g., `{temp_dir}/{src_media_name}.stage1.{src_subtitle_suffix}`       |

### 5\. Stage Configuration [stage_*]

This section can be named `stage_*`, where `*` is a `code` referenced by `task_stages` in `[general]`. For example, if you define `stage_aa`, `stage_bc`, and `stage_7`, you can set `task_stages = bc, aa` in `[general]`. You can define extra stages without using them.

Typically, each task consists of several commands, each defined as a stage.

The default configuration includes seven stages: `stage_0`、`stage_1`、`stage_2`、`stage_3`、`stage_4`、`stage_5`、`stage_6`. Users can override these, but it is not recommended. If you need a new stage, use a new `code` and leave the defaults unused.

Each stage can be configured with the following options:

|   Option    |                                                                                                                                                                                                           Description                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| procedure   | Required. Name of the procedure defined by the program. Options: `convert_file_to_utf8`, `get_audio_stream_idx`, `execute_command`, `shift_source_subtitle_timeline_delay`, `shift_destination_subtitle_timeline_delay`.                                                                                                                                                                                                        |
| input       | Required. Input parameters for the procedure.                                                                                                                                                                                                                                                                                                                                                                                   |
| output_key  | Store the output string in the specified variable (no need to predefine in `[variable]`). Generally, this value does not include `{}`. If `{}` is used, the output will be stored in the variable whose name is the value of the variable inside the braces. For example, if you define a variable `aa=bbb` in `[variable]`, then specifying `{aa}` here will store the output string in the variable named `bbb`, not in `aa`. |
| output_file | Store the output string in the specified file path. Can be used together with `output_key`. If both are omitted, no output is stored.                                                                                                                                                                                                                                                                                           |

#### Procedure definitions:

**Note**: Procedure `shift_source_subtitle_timeline_delay` and `shift_destination_subtitle_timeline_delay` output the content of the subtitle file as a UTF-8 string, so you do not need to use `convert_file_to_utf8` separately.

|                 Procedure                 |                                                                                                                                                                                                          Description                                                                                                                                                                                                          |                                                                    Input                                                                     |                       Output                       |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| convert_file_to_utf8                      | Convert a file to UTF-8 encoding.                                                                                                                                                                                                                                                                                                                                                                                             | File path (usually a subtitle file)                                                                                                          | UTF-8 string of the converted file content         |
| get_audio_stream_idx                      | Get the index of the first audio track.                                                                                                                                                                                                                                                                                                                                                                                       | File path (usually a video/audio file)                                                                                                       | Audio track index                                  |
| execute_command                           | Execute a system command. If the command returns a non-zero exit code, the stage is considered failed.                                                                                                                                                                                                                                                                                                                        | Command string (use double quotes for arguments with spaces; variables like `{XXX}` do not need quotes, even if their values contain spaces) | Output from the system command                     |
| shift_source_subtitle_timeline_delay      | Adjusts the subtitle start time from "matching the video playback start time (which may differ from the video track's start time)" to "matching the start time of the specified audio track." If the input is an audio file instead of a video, the delay is determined from the audio filename (as MKVExtractGUI typically includes the delay in the exported filename). Typically used as a pre-processing step for Sushi.  | Three parameters: `video/audio`, `index number of the audio track`, `subtitle file (any encoding, not just UTF-8)`                           | UTF-8 string of the adjusted subtitle file content |
| shift_destination_subtitle_timeline_delay | Adjusts the subtitle start time from "matching the start time of the specified audio track" to "matching the video playback start time (which may differ from the video track's start time)." If the input is an audio file instead of a video, the delay is determined from the audio filename (as MKVExtractGUI typically includes the delay in the exported filename). Typically used as a post-processing step for Sushi. | Three parameters: `video/audio`, `index number of the audio track`, `subtitle file (any encoding, not just UTF-8)`                           | UTF-8 string of the adjusted subtitle file content |

## License

MIT License. For details, see the [license file](https://lmarena.ai/c/LICENSE).

UI layout inspired by [字幕文件批量改名](https://soft.3dmgame.com/down/286840.html).
