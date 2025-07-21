#!/usr/bin/env python
# coding=utf-8

import asyncio
import configparser
import hashlib
import json
import locale
import queue
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import traceback
from collections import OrderedDict, namedtuple
from datetime import datetime
from io import StringIO
from tkinter import filedialog, messagebox, scrolledtext, ttk

import aiofiles
from charset_normalizer import from_bytes
from tkinterdnd2 import DND_FILES, TkinterDnD


APP_TITLE = "Subtitle Synchro Launcher"

VERSION = 1.0

DEFAULT_CONFIG_CONTENT = """
[general]
subtitle_ext = ass, srt, ssa
media_ext = mkv, mp4, m4a, avi, wmv, flv, rm, rmvb, mov, vob, mpeg, webm, mp3, wav, flac, ape, aac, ac3, opus, ogg, wma, amr
launch_resolution = 1440x600
min_resolution = 860x360
tips_trigger_time_ms = 400
listbox_tips_trigger_time_ms = 600
top_most = yes
checkbox_listbox_repeatable = yes
checkbox_input_file_sorted = yes
default_output_dir =
task_parallel_number = 3
task_stages = 1, 2, 3, 4, 5

[variable]
ffmpeg_exe = ffmpeg
ffprobe_exe = ffprobe
sushi_exe = sushi
#src_subtitle_utf8 = {temp_dir}/{src_media_name}.stage0.{src_subtitle_suffix}
src_subtitle_utf8 = {src_subtitle}
delay_input_subtitle = {temp_dir}/{src_media_name}.stage2.{src_subtitle_suffix}
sushi_output_subtitle = {temp_dir}/{dst_media_name}.stage4.{src_subtitle_suffix}
delay_output_subtitle = {output_dir}/{dst_media_name}.shifted.{src_subtitle_suffix}
src_audio_idx = 1
dst_audio_idx = 1

[stage_0]
procedure = convert_file_to_utf8
input = {src_subtitle}
output_file = {src_subtitle_utf8}

[stage_1]
procedure = get_audio_stream_idx
input = {src_media}
output_key = src_audio_idx

[stage_2]
procedure = shift_source_subtitle_timeline_delay
input = {src_media} {src_audio_idx} {src_subtitle_utf8}
output_file = {delay_input_subtitle}

[stage_3]
procedure = get_audio_stream_idx
input = {dst_media}
output_key = dst_audio_idx

[stage_4]
procedure = execute_command
input = {sushi_exe} --max-window 600 --sample-rate 12000 --temp-dir {temp_dir} --src {src_media} --dst {dst_media} --src-audio {src_audio_idx} --dst-audio {dst_audio_idx} --script {delay_input_subtitle} -o {sushi_output_subtitle}

[stage_5]
procedure = shift_destination_subtitle_timeline_delay
input = {dst_media} {dst_audio_idx} {sushi_output_subtitle}
output_file = {delay_output_subtitle}

[style]
fontname = Microsoft YaHei
label_fontsize = 9
label_tips_fontsize = 9
label_outputdir_icon_fontsize = 10
label_filter_icon_fontsize = 10
listbox_fontsize = 9
entry_fontsize = 10
console_fontname = Microsoft YaHei
console_fontsize = 10
context_menu_fontname = Microsoft YaHei
context_menu_fontsize = 10
button_emoji_fontname = Microsoft YaHei
button_emoji_fontsize = 10
button_execute_fontsize = 12
button_fontsize = 10
button_top = ⤒⤒
button_up = ↑
button_down = ↓
button_bottom = ⤓⤓
button_sort = ⇅
button_add = ➕
button_delete = ✖
button_clear = 🗑
button_topmost = 📌
button_directory = 📁
button_filter = 🔍
color_frame_bg = #f0f0f0
color_label_bg = #f0f0f0
color_label_border = #a0a0a0
color_progressbar = #4a86e8
color_progressbar_bg = #f0f0f0
color_progressbar_trough = #e6e6e6
color_checkbox_bg = #f0f0f0
color_button_font = #333333
color_button_font_active = #0078d7
color_button_topmost_font = #ff2222
color_button_topmost_font_active = #ff8888
color_button_execute_font = #18a24b
color_button_stop_font = #ff2222
color_listbox_font = #000000
color_listbox_bg = #ffffff
color_odd_row_bg = #f5e6ff
color_even_row_bg = #ffffff
color_console_font = #000000
color_console_error_font = #ff0000
color_console_system_font = #0000ff
color_console_bg = #ffffff
color_output_dir_entry_font = #000000
color_output_dir_entry_bg = #ffffff
color_output_dir_entry_height_fix = 0
color_filter_entry_font = #000000
color_filter_entry_bg = #ffffff
color_filter_entry_height_fix = 0
color_tips_font = #000000
color_tips_bg = #ffffe0

[i18n]
description = A universal GUI for adjusting subtitle timelines based on video/audio
title_profile_name = Profile:
startup_logo = For more information, please visit https://github.com/machinewu/SubtitleSynchroLauncher
column_number = #
column_filename = Filename
column_filepath = Path
drop_mask_hits_source = Drag & drop\tSource video/audio or Source subtitle (folders allowed)
drop_mask_hits_destination = Drag & drop\tDestination video/audio (folders allowed)
label_source_media = Source Video/Audio
label_source_subtitle = Source Subtitle
label_destination_media = Destination Video/Audio
label_output_dir = Output Directory:
label_listbox_repeatable = Repeatable
label_input_file_sorted = Sort
label_listbox_repeatable_tips = Whether duplicate files are allowed in the list box
label_input_file_sorted_tips = Whether to sort input files before adding to the list box
label_file_quantity = Total:
filedialog_title_select_file = Select File
filetype_subtitle = Subtitle
filetype_media = Video/Audio
button_top_tips = Move to Top
button_up_tips = Move Up
button_down_tips = Move Down
button_bottom_tips = Move to Bottom
button_filter_label = Filter:
button_filter_tips = Click to filter filenames (remove those not containing)
button_add_tips = Add File
button_sort_tips = Sort
button_delete_tips = Remove Selected
button_clear_tips = Clear All
button_topmost_tips = Always on Top
button_select_directory_tips = Click to select output directory
button_execute = Run
button_stop = Stop
context_menu_copy = Copy
context_menu_select_all = Select All
filedialog_title_output_dir = Select Output Directory
messagebox_title_error = Warning
messagebox_title_exception = Error Occurred
messagebox_content_get_config_file_fail = Failed to read user config file!
messagebox_content_get_section_fail = Section [{}] not found in config file!
messagebox_content_options_without_procedure = No 'procedure' option defined in section [{}] of config file!
messagebox_content_input_quantity_not_match = The quantity of source video/audio, source subtitle, \tand destination video/audio files must be the same!
messagebox_content_same_src_dst_media = The source and destination video/audio paths for Item {} are the same!
messagebox_content_no_input_file = Please set input files!
messagebox_content_output_dir_is_empty = Please set the output directory!
messagebox_content_output_dir_is_file = The output directory path is not a directory!
messagebox_title_rerun = Duplicate Run Prompt
messagebox_content_rerun = The input files are the same as the last successful run. Run again?
messagebox_title_expand_src_input = Expand Source Input Entries
messagebox_content_expand_src_input = Copy source video/audio and subtitle entries \tto match the quantity of destination video/audio?
procedure_undefined_procedure_name = Undefined procedure name: {}
procedure_running_stage = Executing: stage {stage_id} ({procedure})
procedure_stage_process_failure = Execution failed: stage {stage_id} ({procedure})
procedure_stop = Stopped execution: stage {stage_id} ({procedure})
procedure_detect_file_encode = Detected file encoding: {encoding}, confidence: {confidence}
procedure_shift_src_subtitle_timeline_delay = Source audio track has a DELAY of {} ms
procedure_shift_dst_subtitle_timeline_delay = Destination audio track has a DELAY of {} ms
"""

SIMPLE_CHINESE_I18N_CONTENT = """
[i18n]
description = 一个根据视频/音频调整字幕时间轴的通用GUI
title_profile_name = 配置文件:
startup_logo = 想了解更多信息，请访问 https://github.com/machinewu/SubtitleSynchroLauncher
column_number = #
column_filename = 文件名
column_filepath = 路径
drop_mask_hits_source = 拖入\t源视频/音频 或 源字幕 (可以目录)
drop_mask_hits_destination = 拖入\t目标视频/音频 (可以目录)
label_source_media = 源视频/音频
label_source_subtitle = 源字幕
label_destination_media = 目标视频/音频
label_output_dir = 输出目录:
label_listbox_repeatable = 文件可重复
label_input_file_sorted = 输入时排序
label_listbox_repeatable_tips = 列表框里能否有可重复文件
label_input_file_sorted_tips = 是否将输入文件排序后加入列表框
label_file_quantity = 文件数:
filedialog_title_select_file = 选择文件
filetype_subtitle = 字幕
filetype_media = 视频/音频
button_top_tips = 移至顶部
button_up_tips = 上移一行
button_down_tips = 下移一行
button_bottom_tips = 移至底部
button_filter_label = 筛选:
button_filter_tips = 点击筛选文件名(不含有的删除)
button_add_tips = 添加文件
button_sort_tips = 排序
button_delete_tips = 移除选中项
button_clear_tips = 清空
button_topmost_tips = 窗口置顶
button_select_directory_tips = 点击选择输出目录
button_execute = 运   行
button_stop = 停   止
context_menu_copy = 复制
context_menu_select_all = 全选
filedialog_title_output_dir = 选择输出目录
messagebox_title_error = 警告
messagebox_title_exception = 运行出错
messagebox_content_get_config_file_fail = 用户配置文件读取失败！
messagebox_content_get_section_fail = 配置文件中找不到[{}]！
messagebox_content_options_without_procedure = 配置文件中节点[{}]找不到procedure选项的定义！
messagebox_content_input_quantity_not_match = 源视频/音频、源字幕、目标视频/音频三者文件数需要一致！
messagebox_content_same_src_dst_media = 第 {} 项的 源视频/音频 跟 目标视频/音频 路径相同！
messagebox_content_no_input_file = 请设置输入文件！
messagebox_content_output_dir_is_empty = 请设置输出目录！
messagebox_content_output_dir_is_file = 输出目录的路径并非目录！
messagebox_title_rerun = 重复运行提示
messagebox_content_rerun = 输入文件跟上次成功运行时一样，是否再次运行？
messagebox_title_expand_src_input = 扩展源输入条目
messagebox_content_expand_src_input = 是否将源视频/音频、源字幕条目复制\t以扩展至跟目标视频/音频数量一致？
procedure_undefined_procedure_name = 未定义的procedure名字: {}
procedure_running_stage = 正在执行: stage {stage_id} ({procedure})
procedure_stage_process_failure = 执行失败: stage {stage_id} ({procedure})
procedure_stop = 终止执行: stage {stage_id} ({procedure})
procedure_detect_file_encode = 检测到文件的编码为: {encoding}  置信度: {confidence}
procedure_shift_src_subtitle_timeline_delay = 源音轨带了 {} 毫秒延迟
procedure_shift_dst_subtitle_timeline_delay = 目标音轨带了 {} 毫秒延迟
"""

Message = namedtuple("Message", ["task_id", "content", "tag"])


class ListModuleFrame(ttk.Frame):
    def __init__(self, master, accept_types, **kwargs):
        super().__init__(master, style="Border.TFrame", **kwargs)
        app = self.winfo_toplevel()
        general_cfg = app.general_cfg
        style_cfg = app.style_cfg
        i18n = app.i18n
        self.tips_trigger_time_ms = int(general_cfg["listbox_tips_trigger_time_ms"])
        self.ext_filter_set = {
            f".{x.strip().lower()}" for x in general_cfg[f"{accept_types}_ext"].split(",") if x.strip()
        }
        self.file_number_prefix_text = i18n["label_file_quantity"]
        self.filter_var = tk.StringVar()

        container = ttk.Frame(self)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(5, weight=1)

        # listbox and scrollbar
        treeview_container = ttk.Frame(container)
        treeview_container.grid_columnconfigure(0, weight=1)
        treeview_container.grid_rowconfigure(0, weight=1)
        treeview_container.grid(row=0, column=0, rowspan=6, columnspan=2, padx=4, pady=5, sticky=tk.NSEW)
        v_scroll = ttk.Scrollbar(treeview_container, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(treeview_container, orient=tk.HORIZONTAL)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

        self.treeview = ttk.Treeview(
            treeview_container,
            show="headings",
            columns=("number", "name", "path"),
            selectmode=tk.EXTENDED,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            style="Scroll.Treeview",
        )
        self.treeview.grid(row=0, column=0, sticky=tk.NSEW)
        self.treeview.heading("number", text=i18n["column_number"])
        self.treeview.heading("name", text=i18n["column_filename"])
        self.treeview.heading("path", text=i18n["column_filepath"])
        self.treeview.column("number", minwidth=20, width=20, stretch=False, anchor=tk.W)
        self.treeview.column("name", minwidth=100, width=500, stretch=False, anchor=tk.W)
        self.treeview.column("path", minwidth=100, width=400, stretch=False, anchor=tk.W)
        self.treeview.tag_configure("even", background=style_cfg["color_even_row_bg"])
        self.treeview.tag_configure("odd", background=style_cfg["color_odd_row_bg"])
        v_scroll.config(command=self.treeview.yview)
        h_scroll.config(command=self.treeview.xview)
        if self.tips_trigger_time_ms > 0:
            self.tip_window = None
            self.tip_window_schedule_id = None
            self.tip_cell = None
            self.tip_lock = threading.Lock()
            self.treeview.bind("<Motion>", self.show_tips)
            self.treeview.bind("<Leave>", self.hide_tips)

        # listbox right-side buttons
        for rn, cmd in enumerate(("top", "up", "down", "bottom"), 1):
            btn = ttk.Button(
                container,
                text=style_cfg[f"button_{cmd}"],
                width=2,
                style="Emoji.TButton",
                command=lambda x=cmd: self.move_item(x),
            )
            btn.grid(row=rn, column=2, padx=0, pady=(0, 3), sticky=tk.N)
            TipsBind(btn, i18n[f"button_{cmd}_tips"])

        # listbox bottom-left filter box
        bottom_left_container = ttk.Frame(container)
        bottom_left_container.grid(row=6, column=0, sticky=tk.W)
        ttk.Label(bottom_left_container, text=i18n["button_filter_label"]).pack(side=tk.LEFT, padx=(2, 4))
        filter_entry = ttk.Entry(bottom_left_container, textvariable=self.filter_var, style="Filter.TEntry")
        filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0, ipadx=0, ipady=0)
        filter_label = ttk.Label(filter_entry, text=style_cfg["button_filter"], cursor="hand2", style="Filter.TLabel")
        TipsBind(
            filter_label,
            i18n["button_filter_tips"],
            enter_func=lambda e: e.widget.state(["active"]),
            leave_func=lambda e: e.widget.state(["!active"]),
        )
        filter_label.bind("<Button-1>", self.filter_items)
        filter_label.grid(
            row=0,
            column=0,
            padx=(95, 2),
            pady=2,
            ipadx=0,
            ipady=style_cfg["color_filter_entry_height_fix"],
            sticky=tk.E,
        )

        # bottom-right function buttons
        bottom_right_container = ttk.Frame(container)
        bottom_right_container.grid(row=6, column=1, sticky=tk.E)
        self._count_label = ttk.Label(bottom_right_container, text=" ")
        self._count_label.pack(side=tk.LEFT, padx=(3, 0))
        add_btn = ttk.Button(
            bottom_right_container,
            text=style_cfg["button_add"],
            width=2,
            style="Emoji.TButton",
            command=lambda: self.add_files(
                filedialog.askopenfilenames(
                    title=i18n["filedialog_title_select_file"],
                    filetypes=[(i18n[f"filetype_{accept_types}"], sorted(self.ext_filter_set))],
                )
            ),
        )
        add_btn.pack(side=tk.LEFT, padx=(18, 0))
        TipsBind(add_btn, i18n["button_add_tips"])
        sort_btn = ttk.Button(
            bottom_right_container,
            text=style_cfg["button_sort"],
            width=2,
            style="Emoji.TButton",
            command=self.sort_items,
        )
        sort_btn.pack(side=tk.LEFT, padx=(3, 0))
        TipsBind(sort_btn, i18n["button_sort_tips"])
        delete_btn = ttk.Button(
            bottom_right_container,
            text=style_cfg["button_delete"],
            width=2,
            style="Emoji.TButton",
            command=self.delete_selected,
        )
        delete_btn.pack(side=tk.LEFT, padx=(3, 0))
        TipsBind(delete_btn, i18n["button_delete_tips"])
        clear_btn = ttk.Button(
            bottom_right_container,
            text=style_cfg["button_clear"],
            width=2,
            style="Emoji.TButton",
            command=self.clear_all,
        )
        clear_btn.pack(side=tk.LEFT, padx=(3, 0))
        TipsBind(clear_btn, i18n["button_clear_tips"])
        self.update_count()

        # configure the outermost widget last to prevent flickering of inner components
        container.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    def move_item(self, direction):
        selected_items = self.treeview.selection()
        if not selected_items:
            return

        for item in selected_items:
            parent = self.treeview.parent(item)
            children = list(self.treeview.get_children(parent))
            if not children:
                continue
            current_index = children.index(item)
            max_index = len(children) - 1
            if direction == "top":
                new_index = 0
            elif direction == "bottom":
                new_index = max_index
            elif direction == "up":
                new_index = max(0, current_index - 1)
            elif direction == "down":
                new_index = min(max_index, current_index + 1)
            else:
                continue
            self.treeview.move(item, parent, new_index)
        self.update_number()
        self.update_count()

    @staticmethod
    def _item_color_tags(line_number):
        return "even" if line_number % 2 == 0 else "odd"

    @staticmethod
    def _generate_sort_key(values):
        # split the string into a strictly alternating (string, number, string, number, ...) tuple list for sorting
        sort_key = re.findall(r"\D+|\d+", values[1])
        if values[1][0].isdigit():
            sort_key.insert(0, "")

        sort_key = [int(x) if i % 2 else x for i, x in enumerate(sort_key)]
        return (sort_key, values)

    def get_counter(self):
        return len(self.treeview.get_children())

    def get_path_list(self):
        return [self.treeview.item(x, "values")[2] for x in self.treeview.get_children()]

    def update_number(self):
        # update the item numbers and background colors
        for rn, item in enumerate(self.treeview.get_children(), 1):
            values = self.treeview.item(item, "values")
            if values[0] != rn:
                self.treeview.item(item, values=(rn, values[1], values[2]), tags=self._item_color_tags(rn))

    def update_count(self):
        cnt = self.get_counter()
        self.treeview.column("number", width=8 + 8 * len(str(cnt)))
        self.treeview.update_idletasks()
        self._count_label.config(text=f"{self.file_number_prefix_text} {cnt}")

    def filter_items(self, event):
        filter_str = self.filter_var.get()
        if not filter_str:
            return

        self.delete_selected(
            [x for x in self.treeview.get_children() if filter_str not in self.treeview.item(x, "values")[1]]
        )

    def delete_selected(self, selected_items=None):
        if selected_items is None:
            selected_items = self.treeview.selection()

        if not selected_items:
            return

        for item in selected_items:
            self.treeview.delete(item)

        self.update_number()
        self.update_count()

    def clear_all(self):
        self.treeview.delete(*self.treeview.get_children())
        self.update_count()

    def add_files(self, file_paths, force=False):
        items = self.treeview.get_children()
        if not force and self.winfo_toplevel().is_distinct_var.get():
            exist_paths = {self.treeview.item(item, "values")[2] for item in items}
        else:
            exist_paths = None

        data_content = []
        for path in file_paths:
            if os.path.splitext(path)[1].lower() in self.ext_filter_set:
                path = os.path.abspath(path)
                if not exist_paths or path not in exist_paths:
                    data_content.append((None, [0, os.path.basename(path), path]))

        if self.winfo_toplevel().is_path_sort_var.get():
            data_content = sorted([self._generate_sort_key(x[1]) for x in data_content], key=lambda x: x[0])

        for rn, content in enumerate(data_content, len(items) + 1):
            values = content[1]
            values[0] = rn
            self.treeview.insert("", tk.END, values=values, tags=self._item_color_tags(rn))
        self.update_count()

    def sort_items(self):
        items = self.treeview.get_children()
        if not items:
            return
        sorted_content = sorted(
            [self._generate_sort_key(self.treeview.item(x, "values")) for x in items], key=lambda x: x[0]
        )
        for rn, t in enumerate(sorted_content, 1):
            self.treeview.item(items[rn - 1], values=(rn, t[1][1], t[1][2]), tags=self._item_color_tags(rn))

    def show_tips(self, event):
        if self.treeview.identify_region(event.x, event.y) == "cell":
            column = self.treeview.identify_column(event.x)
            col_idx = int(column.replace("#", "")) - 1
            if col_idx >= 1:
                item_id = self.treeview.identify_row(event.y)
                cur_cell = f"{item_id}\x01{column}"
                if self.tip_window:
                    if self.tip_cell == cur_cell:
                        return
                    else:
                        self.tip_window.destroy()
                        self.tip_window = None

                with self.tip_lock:
                    if self.tip_window_schedule_id:
                        self.treeview.after_cancel(self.tip_window_schedule_id)

                    self.tip_window_schedule_id = self.treeview.after(
                        self.tips_trigger_time_ms,
                        lambda: self._show_tips(
                            self.treeview.item(item_id, "values")[col_idx],
                            cur_cell,
                            f"+{event.x_root + 13}+{event.y_root + 10}",
                        ),
                    )
                return
        self.hide_tips(event)

    def _show_tips(self, text, cell_key, geometry):
        with self.tip_lock:
            self.tip_window_schedule_id = None
            self.tip_cell = cell_key

        self.tip_window = tk.Toplevel(self.treeview)
        self.tip_window.overrideredirect(True)
        self.tip_window.lift(self.treeview)
        self.tip_window.attributes("-topmost", True)
        ttk.Label(self.tip_window, text=text, padding=(2, 0), style="Tips.TLabel").pack(anchor=tk.W)
        self.tip_window.geometry(geometry)

    def hide_tips(self, event):
        with self.tip_lock:
            if self.tip_window_schedule_id:
                self.treeview.after_cancel(self.tip_window_schedule_id)
                self.tip_window_schedule_id = None

        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class DragDropMaskFrame(ttk.Frame):
    def __init__(self, master, hint_text, is_update_output_dir=False, **kwargs):
        super().__init__(master, **kwargs)
        self.hint_text = hint_text
        self.is_update_output_dir = is_update_output_dir
        self.font_name = self.winfo_toplevel().style_cfg["fontname"]
        # drag-and-drop mask hint
        self.hint_mask_hide = True
        self.hint_mask = tk.Canvas(self, borderwidth=0, width=0, height=0)
        self.fix_width = self.hint_mask.winfo_width()
        self.fix_height = self.hint_mask.winfo_height()
        tk.Widget.lower(self.hint_mask)
        self.hint_mask.place(relx=0, rely=0)
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<DropEnter>>", self.show_hits)
        self.dnd_bind("<<DropLeave>>", self.hide_hits)
        self.dnd_bind("<<Drop>>", self.on_drop)

    def show_hits(self, event):
        if self.hint_mask_hide:
            self.hint_mask_hide = False
            w = self.winfo_width() - self.fix_width
            h = self.winfo_height() - self.fix_height
            self.hint_mask.delete(tk.ALL)
            self.hint_mask.config(width=w, height=h)
            self.hint_mask.create_rectangle(16, 16, w - 16, h - 16, outline="#000000", width=1, dash=(4, 4))
            self.hint_mask.create_text(w // 2, h // 2, text=self.hint_text, fill="#000000", font=(self.font_name, 16))
            tk.Widget.lift(self.hint_mask)

    def hide_hits(self, event):
        if not self.hint_mask_hide:
            self.hint_mask_hide = True
            tk.Widget.lower(self.hint_mask)
            self.hint_mask.delete(tk.ALL)
            self.hint_mask.config(width=0, height=0)

    def on_drop(self, event):
        self.hide_hits(event)
        show_files = []
        if self.is_update_output_dir and not self.winfo_toplevel().output_dir_var.get():
            first_dir_from_dir = first_dir_from_file = None
        else:
            first_dir_from_dir = first_dir_from_file = ""

        dir_cnt = 0
        for file_path in self.parse_dropped_files(event.data):
            if os.path.isdir(file_path):
                dir_cnt += 1
                if first_dir_from_dir is None:
                    first_dir_from_dir = file_path
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        show_files.append(os.path.join(root, file))
            elif os.path.isfile(file_path):
                if first_dir_from_file is None:
                    first_dir_from_file = os.path.dirname(file_path)
                show_files.append(file_path)

        # pass the file data to each ListModuleFrame object
        for child in self.winfo_children():
            if isinstance(child, ListModuleFrame):
                child.add_files(show_files)

        if not first_dir_from_file:
            # display the parent directory when multiple directories are used as input
            if dir_cnt > 1 and first_dir_from_dir:
                first_dir_from_file = os.path.dirname(first_dir_from_dir)
            else:
                first_dir_from_file = first_dir_from_dir

        if first_dir_from_file:
            # update the output directory entry value
            self.winfo_toplevel().output_dir_var.set(os.path.abspath(first_dir_from_file))

    @staticmethod
    def parse_dropped_files(data):
        files = []
        ch = []
        in_brace = False
        for c in data:
            if c == "{":
                in_brace = True
            elif c == "}" or (c == " " and not in_brace):
                in_brace = False
                if ch:
                    files.append("".join(ch).strip())
                    ch = []
            else:
                ch.append(c)
        if ch:
            files.append("".join(ch).strip())
        return files


class TipsBind:
    def __init__(self, master, tips_text, enter_func=None, leave_func=None):
        self.master = master
        self.tips_text = tips_text
        self.tip_window = None
        self.tip_window_schedule_id = None
        self.enter_func = enter_func
        self.leave_func = leave_func
        self.tips_trigger_time_ms = int(self.master.winfo_toplevel().general_cfg["tips_trigger_time_ms"])
        if self.tips_trigger_time_ms == 0:
            if enter_func:
                self.master.bind("<Enter>", enter_func)
            if leave_func:
                self.master.bind("<Leave>", leave_func)
        else:
            self.master.bind("<Enter>", self.show_tips)
            self.master.bind("<Leave>", self.hide_tips)

    def show_tips(self, event):
        if self.enter_func:
            self.enter_func(event)

        if not self.tip_window_schedule_id:
            self.tip_window_schedule_id = self.master.after(self.tips_trigger_time_ms, self._show_tips)

    def _show_tips(self):
        self.tip_window_schedule_id = None
        if self.tip_window:
            return

        self.tip_window = tk.Toplevel(self.master)
        self.tip_window.overrideredirect(True)
        self.tip_window.lift(self.master)
        self.tip_window.attributes("-topmost", True)
        # multi-line hint
        for line in self.tips_text.split("\n"):
            ttk.Label(self.tip_window, text=line, padding=(2, 0), style="Tips.TLabel").pack(anchor=tk.W)
        self.tip_window.geometry(f"+{self.master.winfo_pointerx() + 13}+{self.master.winfo_pointery() + 13}")

    def hide_tips(self, event):
        if self.leave_func:
            self.leave_func(event)
        if self.tip_window_schedule_id:
            self.master.after_cancel(self.tip_window_schedule_id)
            self.tip_window_schedule_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ProcedureManager:
    def __init__(self, i18n, console, is_realtime_output=False):
        self.i18n = i18n
        self.console = console
        self.is_realtime_output = is_realtime_output
        self.env = os.environ.copy()
        self.shell_encoding = locale.getpreferredencoding()
        self.processes = set()
        self.is_windows_os = sys.platform.startswith("win")
        self.subprocess_extra_args = dict()

        self.env["PYTHONIOENCODING"] = "utf-8"
        self.env["LANG"] = "en_US.UTF-8"
        self.env["LC_ALL"] = "en_US.UTF-8"

        if self.is_windows_os:
            # when running with pythonw, ensure calling the command line won’t trigger a popup window
            self.subprocess_extra_args["creationflags"] = subprocess.CREATE_NO_WINDOW

    def add_path_to_env(self, path):
        separator = ";" if self.is_windows_os else ":"
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        self.env["PATH"] = f"{os.path.abspath(dir_path)}{separator}{os.environ.get('PATH', '')}"

    def stop_all_processes(self):
        while self.processes:
            try:
                self.processes.pop().terminate()
            except KeyError:
                break
            except BaseException:
                pass

    def _decode_subprocess_output(self, text):
        try:
            return text.decode()
        except BaseException:
            try:
                return text.decode(self.shell_encoding)
            except BaseException:
                pass
        return text.decode("raw_unicode_escape", errors="replace")

    async def execute_command(self, task_id, cmd):
        content = None
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            env=self.env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            **self.subprocess_extra_args,
        )
        self.processes.add(proc)
        try:
            if self.is_realtime_output:

                async def output_reader():
                    line_list = []
                    while True:
                        line = await proc.stdout.readline()
                        line = self._decode_subprocess_output(line)
                        line_list.append(line)
                        line = line.rstrip()
                        if not line:
                            break
                        self.console(task_id, line.rstrip())
                    return "".join(line_list)

                gather = await asyncio.gather(output_reader(), proc.wait())
                if not isinstance(gather[0], asyncio.CancelledError):
                    content = gather[0]
            else:
                content, _ = await proc.communicate()
                content = self._decode_subprocess_output(content)
                self.console(task_id, [x.rstrip() for x in content.rstrip().split("\n")])

            return proc.returncode == 0, content
        finally:
            try:
                self.processes.remove(proc)
            except BaseException:
                pass

    async def read_file(self, task_id, file_path, is_output_detect_result=False):
        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()

        exclude_encodings = []
        detect_result = last_detect_result = None
        for encodings in (["utf_8", "gb18030", "big5"], ["utf_16_le", "utf_16_be", "shift_jis", "cp1252"], []):
            # only detect first 10KB
            detect_result = from_bytes(
                data,
                steps=10,
                chunk_size=1024,
                cp_isolation=encodings,
                cp_exclusion=exclude_encodings,
                preemptive_behaviour=True,
                explain=False,
            ).best()
            if detect_result.chaos < 0.1:
                break
            if last_detect_result is None or last_detect_result.chaos > detect_result.chaos:
                last_detect_result = detect_result
            exclude_encodings.extend(encodings)

        if is_output_detect_result:
            self.console(
                task_id,
                self.i18n["procedure_detect_file_encode"].format_map(
                    {
                        "confidence": f"{1 - detect_result.chaos:.2%}",
                        "encoding": detect_result.encoding.replace("_", "-"),
                    }
                ),
                "system",
            )

        return detect_result.encoding, str(detect_result).replace("\r\n", "\n")

    async def get_audio_stream_idx(self, task_id, ffprobe_exe, media_file):
        cmd = [
            ffprobe_exe,
            "-show_entries",
            "stream=codec_type,index",
            "-v",
            "fatal",
            "-print_format",
            "json",
            "-i",
            media_file,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            env=self.env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            **self.subprocess_extra_args,
        )
        content, _ = await proc.communicate()

        if proc.returncode == 0:
            for s in json.loads(self._decode_subprocess_output(content))["streams"]:
                if s["codec_type"] == "audio":
                    return True, str(s["index"])
        return False, None

    @staticmethod
    def _shift_time(time_str, shift_ms, is_srt=False):
        h, m, s = time_str.split(":")
        s, ms = re.split(r"[,.]", s)
        if not is_srt:
            ms = f"{ms}0"[:3]
        total_ms = int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
        total_ms += shift_ms
        if total_ms < 0:
            total_ms = 0
        h, r = divmod(total_ms, 3600000)
        m, r = divmod(r, 60000)
        s, ms = divmod(r, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}" if is_srt else f"{h}:{m:02d}:{s:02d}.{ms // 10:02d}"

    async def shift_subtitle_timeline_delay(
        self, task_id, ffprobe_exe, is_src_media, media_file, audio_idx, subtitle_file
    ):
        cmd = [
            ffprobe_exe,
            "-show_entries",
            "stream=codec_type,index,start_time",
            "-v",
            "fatal",
            "-print_format",
            "json",
            "-i",
            media_file,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            env=self.env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            **self.subprocess_extra_args,
        )
        content, _ = await proc.communicate()

        if proc.returncode == 0:
            audio_idx = int(audio_idx)
            video_start_time = None
            audio_start_time = None
            is_video = False
            delay_ms = None
            for s in json.loads(self._decode_subprocess_output(content))["streams"]:
                if s["codec_type"] == "video":
                    is_video = True
                if "start_time" in s:
                    if audio_start_time is None and s["codec_type"] == "audio" and s["index"] == audio_idx:
                        audio_start_time = float(s["start_time"])
                    elif video_start_time is None and is_video:
                        video_start_time = float(s["start_time"])

            if video_start_time is not None and audio_start_time is not None:
                delay_ms = int((audio_start_time - video_start_time) * 1000)
            elif not is_video and audio_start_time is None:
                # for audio files, use the DELAY|延迟 in the filename to determine the delay value
                match = re.search(r"(?:DELAY|延迟) (-?\d+)(?:ms|毫秒)\.[^.]+$", media_file)
                if match:
                    delay_ms = int(match.group(1))

            if delay_ms is None:
                return False, None

            is_success, content = await self.read_file(task_id, subtitle_file)
            if not is_success:
                return False, None

            if is_src_media:
                # The start time of the source subtitle is based on the video's timeline
                # (with the video's start time as time zero).
                # The subtitle needs to be adjusted to use the audio's original start time as time zero.
                #
                # If the source audio is delayed by 2000ms relative to the video,
                # It means that when the video is at 01:00 (the subtitle is at 01:00), the audio is at 00:58.
                # Therefore, the source subtitle should be shifted by -2000ms.
                self.console(task_id, self.i18n["procedure_shift_src_subtitle_timeline_delay"].format(delay_ms))
                delay_ms = -delay_ms
            else:
                # The start time of the processed subtitle (output by sushi) is based on the timeline where
                # the audio's original start time is zero.
                # The subtitle needs to be adjusted to the timeline where the video's start time is zero.
                #
                # If the destination audio is delayed by 2000ms relative to the video,
                # when the video is at 01:00, it means the audio is at 00:58 (and the processed subtitle is at 00:58).
                # Therefore, the processed subtitle should be shifted by +2000ms.
                self.console(task_id, self.i18n["procedure_shift_dst_subtitle_timeline_delay"].format(delay_ms))

            if subtitle_file.lower().endswith(".srt"):
                if delay_ms != 0 or re.search(r"\d+:\d{2}:\d{2}\.\d{3}", content):
                    pattern = re.compile(
                        r"^ *(\d+:\d{2}:\d{2}[,.]\d{3}) --> (\d+:\d{2}:\d{2}[,.]\d{3})", flags=re.MULTILINE
                    )
                    content = pattern.sub(
                        lambda m: f"{self._shift_time(m.group(1), delay_ms, is_srt=True)} --> "
                        f"{self._shift_time(m.group(2), delay_ms, is_srt=True)}",
                        content,
                    )
            else:
                # Non-SRT subtitles do not support millisecond precision, so the delay time is rounded
                delay_ms = (delay_ms + 5) // 10 * 10
                if delay_ms != 0:
                    pattern = re.compile(
                        r"^ *((?:Dialogue|Comment):.*?,)(\d+:\d{2}:\d{2}\.\d{2}),(\d+:\d{2}:\d{2}\.\d{2})",
                        flags=re.MULTILINE,
                    )
                    content = pattern.sub(
                        lambda m: f"{m.group(1)}{self._shift_time(m.group(2), delay_ms)},"
                        f"{self._shift_time(m.group(3), delay_ms)}",
                        content,
                    )

            return True, content


class TaskManager:
    class ReplaceSafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    def __init__(self, app):
        self.i18n = app.i18n
        self.is_create_temp_dir = app.is_create_temp_dir
        self.task_stages = app.task_stages
        self.parallel_number = app.parallel_number
        self.stage_variable = app.stage_variable
        self.message_queue = app.message_queue
        self.subtitle_exts = {f".{x.strip().lower()}" for x in app.general_cfg[f"subtitle_ext"].split(",") if x.strip()}
        self.tasks = None
        self.tasks_gather = None
        self.semaphore = None
        self.thread = None
        self.is_abort = False
        self.procedure_manager = ProcedureManager(self.i18n, self.console, self.parallel_number == 1)
        self.update_process = lambda: app.update_process()
        self.finished_callback = lambda: app.reset_execute_button()

        for k, v in self.stage_variable.items():
            if k.endswith("_exe"):
                # add values with keys in the XXX_exe format to the environment PATH
                self.procedure_manager.add_path_to_env(v)

    def console(self, task_id, content, tag=None):
        if isinstance(content, list):
            self.message_queue.batch_put([Message(task_id, x, tag) for x in content])
        else:
            self.message_queue.put(Message(task_id, content, tag))

    def stop_tasks(self):
        self.is_abort = True
        self.procedure_manager.stop_all_processes()

    def start_tasks(self, output_dir, task_paths_list):
        self.thread = threading.Thread(
            target=lambda: asyncio.run(self._start_tasks_main(output_dir, task_paths_list)), daemon=True
        )
        self.thread.start()

    async def _start_tasks_main(self, output_dir, task_paths_list):
        # the SEMAPHORE should be created in the thread where it will be used
        self.is_abort = False
        self.semaphore = asyncio.Semaphore(self.parallel_number)
        self.tasks = [self._process(output_dir, *x) for x in task_paths_list]
        self.tasks_gather = await asyncio.gather(*self.tasks)

        stage_cnt = len(self.task_stages)
        self.console(0, f'\n{"*" * 40}\n   task | stage | target media\n{"-" * 30}')
        for p, finished_stage_cnt in zip(task_paths_list, self.tasks_gather):
            if isinstance(finished_stage_cnt, BaseException):
                finished_stage_cnt = 0
            self.console(
                0,
                f'{"✔" if finished_stage_cnt == stage_cnt else "✖"} {p[0]:^5}|'
                f"{finished_stage_cnt:>3}/{stage_cnt:<3}| {os.path.basename(p[3])}",
            )
        self.console(0, f'\n{"*" * 40}')

        self.thread = None
        self.tasks = None
        self.tasks_gather = None
        self.semaphore = None
        self.finished_callback()

    async def _process(self, output_dir, task_id, src_media_path, src_subtitle_path, dst_media_path):
        finished_stage_cnt = 0
        async with self.semaphore:
            if self.is_abort:
                return finished_stage_cnt

            try:
                default_vars_map = self.ReplaceSafeDict(
                    {
                        "output_dir": output_dir,
                        "task_id": task_id,
                        "temp_dir": os.path.join(output_dir, f"_tmp{datetime.now():%y%m%d%H%M%S}-{task_id}"),
                    }
                )
                for k, path in {
                    "src_media": src_media_path,
                    "src_subtitle": src_subtitle_path,
                    "dst_media": dst_media_path,
                }.items():
                    name_no_suffix, suffix = os.path.splitext(os.path.basename(path))
                    default_vars_map[k] = path
                    default_vars_map[f"{k}_name"] = name_no_suffix
                    default_vars_map[f"{k}_suffix"] = suffix[1:]
                    default_vars_map[f"{k}_dir"] = os.path.dirname(path)

                vars_map = default_vars_map.copy()
                for k, v in self.stage_variable.items():
                    # prevent default variable overwriting
                    if k not in default_vars_map:
                        # don't format the values of keys in the XXX_exe format
                        vars_map[k] = v if k.endswith("_exe") else v.format_map(vars_map)

                if self.is_create_temp_dir:
                    os.makedirs(vars_map["temp_dir"], exist_ok=True)

                for stage_id, stage in self.task_stages.items():
                    if self.is_abort:
                        return finished_stage_cnt
                    stage = {
                        k: ([x.format_map(vars_map) for x in v] if isinstance(v, list) else v.format_map(vars_map))
                        for k, v in stage.items()
                    }
                    procedure = stage["procedure"]
                    self.console(
                        task_id,
                        self.i18n["procedure_running_stage"].format_map({"stage_id": stage_id, "procedure": procedure}),
                        "system",
                    )

                    if procedure == "execute_command":
                        is_success, content = await self.procedure_manager.execute_command(task_id, stage["input"])
                    elif procedure == "get_audio_stream_idx":
                        is_success, content = await self.procedure_manager.get_audio_stream_idx(
                            task_id, vars_map["ffprobe_exe"], *stage["input"]
                        )
                    elif procedure == "shift_source_subtitle_timeline_delay":
                        is_success, content = await self.procedure_manager.shift_subtitle_timeline_delay(
                            task_id, vars_map["ffprobe_exe"], True, *stage["input"]
                        )
                    elif procedure == "shift_destination_subtitle_timeline_delay":
                        is_success, content = await self.procedure_manager.shift_subtitle_timeline_delay(
                            task_id, vars_map["ffprobe_exe"], False, *stage["input"]
                        )
                    elif procedure == "convert_file_to_utf8":
                        is_success, content = await self.procedure_manager.read_file(
                            task_id, *stage["input"], is_output_detect_result=True
                        )
                    else:
                        raise AttributeError(self.i18n["procedure_undefined_procedure_name"].format(procedure))

                    if self.is_abort:
                        raise asyncio.CancelledError(
                            self.i18n["procedure_stop"].format_map({"stage_id": stage_id, "procedure": procedure})
                        )

                    if not is_success:
                        raise RuntimeError(
                            self.i18n["procedure_stage_process_failure"].format_map(
                                {"stage_id": stage_id, "procedure": procedure}
                            )
                        )

                    output_key = stage.get("output_key", None)
                    if output_key and output_key not in default_vars_map and not output_key.endswith("_exe"):
                        vars_map[output_key] = content

                    output_file = stage.get("output_file", None)
                    if output_file:
                        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
                            f.write(content)
                            # ensure the subtitle file ends with a blank line
                            if (
                                content
                                and content[-1] != "\n"
                                and os.path.splitext(output_file)[1].lower() in self.subtitle_exts
                            ):
                                f.write("\n")

                    self.update_process()
                    finished_stage_cnt += 1
            except asyncio.CancelledError as e:
                self.console(task_id, e, "error")
            except BaseException:
                self.console(task_id, traceback.format_exc(), "error")
            finally:
                if self.is_create_temp_dir:
                    shutil.rmtree(vars_map["temp_dir"])
        return finished_stage_cnt


class Application(TkinterDnD.Tk):
    class EscapeInterpolation(configparser.Interpolation):
        def before_get(self, parser, section, option, value, defaults):
            # return value.encode('raw_unicode_escape').decode('unicode_escape')
            return value.replace("\t", "\n")

    class MessageQueue(queue.SimpleQueue):
        def __init__(self, send_trigger_func):
            super().__init__()
            self.send_trigger_func = send_trigger_func
            self._lock = threading.Lock()

        def put(self, item, block=True, timeout=None):
            with self._lock:
                super().put(item, block=block, timeout=timeout)
            self.send_trigger_func()

        def batch_put(self, items, block=True, timeout=None):
            with self._lock:
                for item in items:
                    super().put(item, block=block, timeout=timeout)
            self.send_trigger_func()

    class ReadOnlyScrolledText(scrolledtext.ScrolledText):
        def __init__(self, message_queue, master=None, **kwargs):
            super().__init__(master, **kwargs)
            self.message_queue = message_queue
            self.scroll_pending = False

            self.bind("<KeyPress>", self._key_press_event)
            self.bind("<Button-2>", self._block_event)
            self.bind("<<Paste>>", self._block_event)
            self.bind("<<Cut>>", self._block_event)
            self.bind("<<Clear>>", self._block_event)

        def _block_event(self, event):
            return "break"

        def _key_press_event(self, event):
            # ctrl button: event.state == 4
            if (event.state & 0x04) and event.keysym.lower() in ("a", "c", "insert"):
                return None

            if event.keysym in (
                "Left",
                "Right",
                "Up",
                "Down",
                "Home",
                "End",
                "Prior",
                "Next",
                "Shift_L",
                "Shift_R",
                "Control_L",
                "Control_R",
                "Alt_L",
                "Alt_R",
                "Caps_Lock",
                "Num_Lock",
            ):
                return None

            return "break"

        def delay_scroll(self):
            if not self.scroll_pending:
                self.scroll_pending = True
                self.after(50, self.do_scroll)

        def do_scroll(self):
            self.scroll_pending = False
            self.see(tk.END)

        def read_message(self, event=None):
            # since tag can be None, so last_tag is initialized to a value where tag cannot appear, like []
            last_tag = batch_content = []
            cnt = 0
            try:
                while True:
                    message = self.message_queue.get_nowait()
                    task_key = f"[#{message.task_id}] " if message.task_id > 0 else ""

                    if batch_content and (last_tag != message.tag or cnt > 7):
                        self.insert(tk.END, "\n".join(batch_content) + "\n", last_tag)
                        self.delay_scroll()
                        batch_content = []
                        cnt = 0
                    batch_content.append(f"{task_key}{message.content}")
                    last_tag = message.tag
                    cnt += 1
            except queue.Empty:
                pass

            if batch_content:
                self.insert(tk.END, "\n".join(batch_content) + "\n", last_tag)
                self.delay_scroll()

    def __init__(self, config_file):
        super().__init__()
        if not self._prepare_configure(config_file):
            return

        self._style_setting()
        self._create_widgets()
        self.scroll_console.insert(tk.END, "𝕊𝕦𝕓𝕥𝕚𝕥𝕝𝕖 𝕊𝕪𝕟𝕔𝕙𝕣𝕠 𝕃𝕒𝕦𝕟𝕔𝕙𝕖𝕣\n", "logo")
        self.scroll_console.insert(tk.END, f"{self.i18n['startup_logo']}", "system")

    def _prepare_configure(self, config_file):
        ini_config = configparser.ConfigParser(
            interpolation=self.EscapeInterpolation(), delimiters=("="), comment_prefixes=(";", "#"), strict=True
        )
        # load the default configuration first
        ini_config.read_file(StringIO(DEFAULT_CONFIG_CONTENT))

        lang = locale.getlocale()[0]
        if not lang:
            try:
                lang = locale.getdefaultlocale()[0]
            except BaseException:
                pass
        if lang and (lang.upper().startswith("CHINESE") or lang.startswith("zh_")):
            ini_config.read_file(StringIO(SIMPLE_CHINESE_I18N_CONTENT))
        self.profile_name = None

        # then load the user configuration to override
        if config_file and ini_config.read(config_file, encoding="utf-8-sig"):
            self.profile_name = os.path.basename(config_file)

        self.i18n = ini_config["i18n"]
        self.style_cfg = ini_config["style"]
        self.general_cfg = ini_config["general"]
        self.output_dir_var = tk.StringVar(
            value=(
                os.path.abspath(self.general_cfg["default_output_dir"])
                if self.general_cfg["default_output_dir"]
                else ""
            )
        )
        self.is_distinct_var = tk.BooleanVar(
            value=self.general_cfg["checkbox_listbox_repeatable"].lower() in ("no", "false", "n", "0")
        )
        self.is_path_sort_var = tk.BooleanVar(
            value=self.general_cfg["checkbox_input_file_sorted"].lower() not in ("no", "false", "n", "0")
        )
        self.current_inputs_hash = None
        self.last_inputs_hash = ""
        self.task_progress = tk.IntVar(value=0)
        self.is_create_temp_dir = False
        self.task_stages = OrderedDict()
        self.parallel_number = int(self.general_cfg["task_parallel_number"])

        for stage_id in self.general_cfg["task_stages"].split(","):
            section = f"stage_{stage_id.strip()}"
            if not ini_config.has_section(section):
                messagebox.showerror(
                    self.i18n["messagebox_title_error"],
                    self.i18n["messagebox_content_get_section_fail"].format(section),
                )
                return False

            items = dict(ini_config[section])
            if "procedure" not in items:
                messagebox.showerror(
                    self.i18n["messagebox_title_error"],
                    self.i18n["messagebox_content_options_without_procedure"].format(section),
                )
                return False

            for value in items.values():
                if "{temp_dir}" in value:
                    self.is_create_temp_dir = True
                    break

            if "input" in items:
                items["input"] = shlex.split(items["input"], posix=False)
            self.task_stages[stage_id.strip()] = items
        self.stage_variable = OrderedDict(ini_config["variable"])

        if not self.is_create_temp_dir:
            for value in self.stage_variable.values():
                if "{temp_dir}" in value:
                    self.is_create_temp_dir = True
                    break

        self.message_queue = self.MessageQueue(lambda: self.after(0, self.scroll_console.read_message))
        self.task_manager = TaskManager(self)
        return True

    def _style_setting(self):
        s = ttk.Style()
        # s.theme_use('clam')
        # self.tk.call('source', os.path.join(os.path.dirname(__file__), 'azure.tcl'))
        # self.tk.call('set_theme', 'light')
        s.configure("TFrame", background=self.style_cfg["color_frame_bg"])
        s.configure("Border.TFrame", borderwidth=1, highlightthickness=0, relief=tk.GROOVE)

        s.configure(
            "TLabel",
            font=(self.style_cfg["fontname"], self.style_cfg["label_fontsize"]),
            background=self.style_cfg["color_label_bg"],
        )
        s.configure("Border.Label", borderwidth=2, relief=tk.GROOVE, background=self.style_cfg["color_label_border"])
        s.configure(
            "Tips.TLabel",
            borderwidth=1,
            relief=tk.GROOVE,
            foreground=self.style_cfg["color_tips_font"],
            background=self.style_cfg["color_tips_bg"],
            font=(self.style_cfg["fontname"], self.style_cfg["label_tips_fontsize"]),
        )
        s.configure(
            "OutputDir.TLabel",
            padding=0,
            borderwidth=0,
            relief=tk.FLAT,
            foreground=self.style_cfg["color_output_dir_entry_font"],
            background=self.style_cfg["color_output_dir_entry_bg"],
            font=(self.style_cfg["fontname"], self.style_cfg["label_outputdir_icon_fontsize"]),
        )
        s.map(
            "OutputDir.TLabel",
            foreground=[("active", self.style_cfg["color_button_font_active"])],
            background=[("active", self.style_cfg["color_output_dir_entry_bg"])],
        )
        s.configure(
            "Filter.TLabel",
            padding=0,
            borderwidth=0,
            relief=tk.FLAT,
            foreground=self.style_cfg["color_filter_entry_font"],
            background=self.style_cfg["color_filter_entry_bg"],
            font=(self.style_cfg["fontname"], self.style_cfg["label_filter_icon_fontsize"]),
        )
        s.map(
            "Filter.TLabel",
            foreground=[("active", self.style_cfg["color_button_font_active"])],
            background=[("active", self.style_cfg["color_filter_entry_bg"])],
        )

        s.configure(
            "TButton",
            foreground=self.style_cfg["color_button_font"],
            font=(self.style_cfg["fontname"], self.style_cfg["button_fontsize"]),
        )
        s.map("TButton", foreground=[("active", self.style_cfg["color_button_font_active"])])
        s.configure(
            "Emoji.TButton", font=(self.style_cfg["button_emoji_fontname"], self.style_cfg["button_emoji_fontsize"])
        )
        s.configure(
            "Topmost.TButton",
            relief=tk.RAISED,
            font=(self.style_cfg["button_emoji_fontname"], self.style_cfg["button_emoji_fontsize"]),
        )
        s.configure("Pressed.Topmost.TButton", relief=tk.SUNKEN, foreground=self.style_cfg["color_button_topmost_font"])
        s.map("Pressed.Topmost.TButton", foreground=[("active", self.style_cfg["color_button_topmost_font_active"])])
        s.configure(
            "Execute.TButton",
            foreground=self.style_cfg["color_button_execute_font"],
            font=(self.style_cfg["fontname"], self.style_cfg["button_execute_fontsize"], "bold"),
        )
        s.configure("Stop.Execute.TButton", foreground=self.style_cfg["color_button_stop_font"])

        s.configure("TCheckbutton", background=self.style_cfg["color_checkbox_bg"])
        s.map("TCheckbutton", background=[("active", self.style_cfg["color_checkbox_bg"])])

        s.configure(
            "Scroll.Treeview",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
            foreground=self.style_cfg["color_listbox_font"],
            background=self.style_cfg["color_listbox_bg"],
            font=(self.style_cfg["fontname"], self.style_cfg["listbox_fontsize"]),
        )
        # remove border components
        s.layout("Scroll.Treeview", [("Treeview.treearea", {"sticky": tk.NSEW})])

        s.configure("TEntry", font=(self.style_cfg["fontname"], self.style_cfg["entry_fontsize"]))
        s.configure(
            "Filter.TEntry",
            padding=(3, 1, 22, 0),
            foreground=self.style_cfg["color_filter_entry_font"],
            background=self.style_cfg["color_filter_entry_bg"],
        )
        s.configure(
            "OutputDir.TEntry",
            padding=(21, 1, 2, 0),
            foreground=self.style_cfg["color_output_dir_entry_font"],
            background=self.style_cfg["color_output_dir_entry_bg"],
        )

        s.configure(
            "Task.Horizontal.TProgressbar",
            foreground=self.style_cfg["color_progressbar"],
            troughcolor=self.style_cfg["color_progressbar_trough"],
            background=self.style_cfg["color_progressbar_bg"],
        )

    def _create_widgets(self):
        self.title(f"{APP_TITLE} v{VERSION}  [{self.i18n['title_profile_name']} {self.profile_name}]")
        w, h = (int(x) for x in self.general_cfg["launch_resolution"].split("x"))
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth() - w) // 2}+{(self.winfo_screenheight() - h) // 2}")
        self.minsize(*self.general_cfg["min_resolution"].split("x"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = ttk.Frame(self)
        self.main_frame = main_frame
        main_frame.grid_rowconfigure(0, weight=5)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, padx=0, pady=0, stick=tk.NSEW)
        input_frame.grid_columnconfigure(0, weight=2)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        src_frame = DragDropMaskFrame(input_frame, self.i18n["drop_mask_hits_source"])
        src_frame.grid_columnconfigure(0, weight=1)
        src_frame.grid_columnconfigure(1, weight=1)
        src_frame.grid_rowconfigure(0, weight=1)
        src_frame.grid(row=0, column=0, padx=0, pady=0, sticky=tk.NSEW)

        dst_frame = DragDropMaskFrame(input_frame, self.i18n["drop_mask_hits_destination"], is_update_output_dir=True)
        dst_frame.grid_columnconfigure(0, weight=1)
        dst_frame.grid_rowconfigure(0, weight=1)
        dst_frame.grid(row=0, column=1, padx=0, pady=0, sticky=tk.NSEW)

        self.src_media_frame = ListModuleFrame(src_frame, "media")
        self.src_media_frame.grid(row=0, column=0, padx=5, pady=(10, 0), sticky=tk.NSEW)
        self.src_subtitle_frame = ListModuleFrame(src_frame, "subtitle")
        self.src_subtitle_frame.grid(row=0, column=1, padx=5, pady=(10, 0), sticky=tk.NSEW)
        self.dst_media_frame = ListModuleFrame(dst_frame, "media")
        self.dst_media_frame.grid(row=0, column=0, padx=5, pady=(10, 0), sticky=tk.NSEW)
        ttk.Label(src_frame, text=self.i18n["label_source_media"]).grid(row=0, column=0, padx=10, ipadx=1, sticky=tk.NW)
        ttk.Label(src_frame, text=self.i18n["label_source_subtitle"]).grid(
            row=0, column=1, padx=10, ipadx=1, sticky=tk.NW
        )
        ttk.Label(dst_frame, text=self.i18n["label_destination_media"]).grid(
            row=0, column=0, padx=10, ipadx=1, sticky=tk.NW
        )

        # progressbar
        progressbar_frame = ttk.Frame(main_frame, height=12)
        progressbar_frame.grid_propagate(False)
        progressbar_frame.grid_rowconfigure(0, weight=1)
        progressbar_frame.grid_columnconfigure(0, weight=1)
        progressbar_frame.grid(row=1, column=0, padx=5, pady=(3, 0), stick=tk.EW)
        self.progressbar = ttk.Progressbar(
            progressbar_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode="determinate",
            variable=self.task_progress,
            style="Task.Horizontal.TProgressbar",
        )
        self.progressbar.grid(row=0, column=0, padx=(0, 1), pady=0, stick=tk.NSEW)

        # output directory config area
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, padx=0, pady=3, stick=tk.EW)

        # always-on-top button
        self.topmost_btn = ttk.Button(
            bottom_frame,
            text=self.style_cfg["button_topmost"],
            width=3,
            style="Topmost.TButton",
            command=self._toggle_topmost,
        )
        self.topmost_btn.pack(side=tk.LEFT, padx=(4, 0))
        TipsBind(self.topmost_btn, self.i18n["button_topmost_tips"])
        if self.general_cfg["top_most"].lower() not in ("no", "false", "n", "0"):
            self._toggle_topmost()

        # output directory entry
        ttk.Label(bottom_frame, text=self.i18n["label_output_dir"]).pack(side=tk.LEFT, padx=(8, 5))
        output_dir_entry = ttk.Entry(bottom_frame, style="OutputDir.TEntry", textvariable=self.output_dir_var)
        output_dir_entry.bind("<FocusOut>", self._format_output_path)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0, ipadx=0, ipady=0)
        filedialog_label = ttk.Label(
            output_dir_entry, text=self.style_cfg["button_directory"], cursor="hand2", style="OutputDir.TLabel"
        )
        TipsBind(
            filedialog_label,
            self.i18n["button_select_directory_tips"],
            enter_func=lambda e: e.widget.state(["active"]),
            leave_func=lambda e: e.widget.state(["!active"]),
        )
        filedialog_label.bind("<Button-1>", self._select_output_path)
        filedialog_label.grid(
            row=0,
            column=0,
            padx=(2, 0),
            pady=2,
            ipadx=0,
            ipady=self.style_cfg["color_output_dir_entry_height_fix"],
            sticky=tk.W,
        )

        # checkbox
        sorted_checkbox = ttk.Checkbutton(
            bottom_frame,
            text=self.i18n["label_input_file_sorted"],
            variable=self.is_path_sort_var,
            onvalue=True,
            offvalue=False,
        )
        sorted_checkbox.pack(side=tk.LEFT, padx=(18, 0))
        TipsBind(sorted_checkbox, self.i18n["label_input_file_sorted_tips"])
        repeatable_checkbox = ttk.Checkbutton(
            bottom_frame,
            text=self.i18n["label_listbox_repeatable"],
            variable=self.is_distinct_var,
            onvalue=False,
            offvalue=True,
        )
        repeatable_checkbox.pack(side=tk.LEFT, padx=(8, 0))
        TipsBind(repeatable_checkbox, self.i18n["label_listbox_repeatable_tips"])

        # run button
        self.execute_btn = ttk.Button(
            bottom_frame, text=self.i18n["button_execute"], width=10, style="Execute.TButton", command=self._execute
        )
        self.execute_btn.pack(side=tk.LEFT, padx=(13, 5))

        # output console
        scrolledtext_frame = ttk.Frame(main_frame, style="Border.TFrame")
        scrolledtext_frame.grid(row=3, column=0, padx=4, pady=(0, 3), stick=tk.NSEW)
        self.scroll_console = self.ReadOnlyScrolledText(
            message_queue=self.message_queue,
            master=scrolledtext_frame,
            wrap=tk.WORD,
            width=40,
            height=8,
            border=0,
            padx=4,
            pady=4,
            foreground=self.style_cfg["color_console_font"],
            bg=self.style_cfg["color_console_bg"],
            font=(self.style_cfg["console_fontname"], self.style_cfg["console_fontsize"]),
        )
        self.scroll_console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.scroll_console.tag_configure("logo", foreground="#00d999", font=("Arial", 18))
        self.scroll_console.tag_configure("normal", foreground=self.style_cfg["color_console_font"])
        self.scroll_console.tag_configure("error", foreground=self.style_cfg["color_console_error_font"])
        self.scroll_console.tag_configure("system", foreground=self.style_cfg["color_console_system_font"])

        self.context_menu = tk.Menu(self.scroll_console, tearoff=False)
        self.context_menu.add_command(
            label=self.i18n["context_menu_copy"],
            font=(self.style_cfg["context_menu_fontname"], self.style_cfg["context_menu_fontsize"]),
            command=self._copy_selected_text,
        )
        self.context_menu.add_command(
            label=self.i18n["context_menu_select_all"],
            font=(self.style_cfg["context_menu_fontname"], self.style_cfg["context_menu_fontsize"]),
            command=self._select_all_text,
        )
        self.scroll_console.bind("<Button-3>", self._show_context_menu)

        # configure the outermost widget last to prevent flickering of inner components
        main_frame.grid(row=0, column=0, padx=5, pady=(4, 5), stick=tk.NSEW)

    def reset_execute_button(self):
        self.execute_btn.configure(text=self.i18n["button_execute"], style="Execute.TButton")
        self.execute_btn.state(["!disabled"])
        if self.task_progress.get() == self.progressbar["maximum"]:
            self.last_inputs_hash = self.current_inputs_hash

    def update_process(self):
        self.after(0, lambda: self.task_progress.set(self.task_progress.get() + 1))

    def _toggle_topmost(self):
        if self.topmost_btn["style"] == "Pressed.Topmost.TButton":
            # normal status
            self.attributes("-topmost", False)
            self.topmost_btn.configure(style="Topmost.TButton")
            self.topmost_btn.state(["!pressed"])
        else:
            # pressed status
            self.attributes("-topmost", True)
            self.topmost_btn.configure(style="Pressed.Topmost.TButton")
            self.topmost_btn.state(["pressed"])

    def _format_output_path(self, event):
        path = self.output_dir_var.get().strip()
        if path:
            self.output_dir_var.set(os.path.abspath(path))
        else:
            self.output_dir_var.set("")

    def _select_output_path(self, event):
        dir_path = filedialog.askdirectory(title=self.i18n["filedialog_title_output_dir"])
        if dir_path:
            self.output_dir_var.set(os.path.abspath(dir_path))

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
        return "break"

    def _copy_selected_text(self):
        try:
            selected_text = self.scroll_console.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # text not selected
            pass

    def _select_all_text(self):
        self.scroll_console.focus()
        self.scroll_console.tag_add(tk.SEL, "1.0", tk.END)
        self.scroll_console.see(tk.END)

    def _execute(self):
        if self.execute_btn.cget("text") == self.i18n["button_execute"]:
            self.execute_btn.state(["disabled"])
            if self._task_prepare():
                self.execute_btn.configure(text=self.i18n["button_stop"], style="Stop.Execute.TButton")
                self.execute_btn.state(["!disabled"])
                self.task_manager.start_tasks(
                    self.output_dir_var.get(),
                    list(
                        zip(
                            range(1, self.src_media_frame.get_counter() + 1),
                            self.src_media_frame.get_path_list(),
                            self.src_subtitle_frame.get_path_list(),
                            self.dst_media_frame.get_path_list(),
                        )
                    ),
                )
            else:
                self.execute_btn.state(["!disabled"])
        else:
            # stop button
            self.execute_btn.state(["disabled"])
            self.task_manager.stop_tasks()

    def _task_prepare(self):
        src_media_path_list = self.src_media_frame.get_path_list()
        src_subtitle_path_list = self.src_subtitle_frame.get_path_list()
        dst_media_path_list = self.dst_media_frame.get_path_list()
        task_num = len(dst_media_path_list)

        if len(src_media_path_list) != task_num or len(src_subtitle_path_list) != task_num:
            if len(src_media_path_list) == 1 and len(src_subtitle_path_list) == 1 and task_num > 1:
                if messagebox.askokcancel(
                    self.i18n["messagebox_title_expand_src_input"], self.i18n["messagebox_content_expand_src_input"]
                ):
                    self.src_media_frame.add_files(self.src_media_frame.get_path_list() * (task_num - 1), force=True)
                    self.src_subtitle_frame.add_files(
                        self.src_subtitle_frame.get_path_list() * (task_num - 1), force=True
                    )
                    src_media_path_list = self.src_media_frame.get_path_list()
                    src_subtitle_path_list = self.src_subtitle_frame.get_path_list()
                else:
                    return False
            else:
                messagebox.showwarning(
                    self.i18n["messagebox_title_error"], self.i18n["messagebox_content_input_quantity_not_match"]
                )
                return False

        if task_num == 0:
            messagebox.showwarning(self.i18n["messagebox_title_error"], self.i18n["messagebox_content_no_input_file"])
            return False

        conflict_task_ids = []
        for i in range(task_num):
            if src_media_path_list[i] == dst_media_path_list[i]:
                conflict_task_ids.append(f"{i + 1}")

        if conflict_task_ids:
            messagebox.showwarning(
                self.i18n["messagebox_title_error"],
                self.i18n["messagebox_content_same_src_dst_media"].format(",".join(conflict_task_ids)),
            )
            return False

        # check whether the input is the same as the last run
        sha1 = hashlib.sha1()
        sha1.update(
            "\x02".join(
                ["\x01".join(x) for x in [src_media_path_list, src_subtitle_path_list, dst_media_path_list]]
            ).encode("utf-8")
        )
        self.current_inputs_hash = sha1.hexdigest()
        if self.last_inputs_hash == self.current_inputs_hash and not messagebox.askyesno(
            self.i18n["messagebox_title_rerun"], self.i18n["messagebox_content_rerun"]
        ):
            return False

        output_dir_path = self.output_dir_var.get()
        if not output_dir_path:
            messagebox.showwarning(
                self.i18n["messagebox_title_error"], self.i18n["messagebox_content_output_dir_is_empty"]
            )
            return False

        if os.path.exists(output_dir_path):
            if not os.path.isdir(output_dir_path):
                messagebox.showwarning(
                    self.i18n["messagebox_title_error"], self.i18n["messagebox_content_output_dir_is_file"]
                )
                return False
        else:
            try:
                os.makedirs(self.output_dir_var.get())
            except BaseException:
                messagebox.showerror(self.i18n["messagebox_title_exception"], traceback.format_exc())
                return False

        self.task_progress.set(0)
        self.progressbar["maximum"] = task_num * len(self.task_stages)
        self.scroll_console.delete(1.0, tk.END)
        return True


def main(config_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")):
    app = Application(config_path)
    app.mainloop()


if __name__ == "__main__":
    main()
