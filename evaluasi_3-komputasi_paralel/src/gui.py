import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from scheduler import Scheduler


def get_default_dataset_path():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_dir, 'data', 'OnlineRetail.csv')


class ParallelSchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Parallel Job Scheduler')
        self.geometry('760x580')
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.update()
        self.attributes('-topmost', False)
        self.message_queue = queue.Queue()
        self.scheduler_thread = None
        self._build_widgets()
        self._schedule_queue()

    def _build_widgets(self):
        frame = ttk.Frame(self, padding=(12, 12, 12, 12))
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text='Dataset CSV').grid(row=0, column=0, sticky='w')
        self.dataset_path = tk.StringVar(value=get_default_dataset_path())
        entry = ttk.Entry(frame, textvariable=self.dataset_path, width=72)
        entry.grid(row=1, column=0, columnspan=3, sticky='we', pady=(4, 8))

        browse_button = ttk.Button(frame, text='Pilih File', command=self._choose_file)
        browse_button.grid(row=1, column=3, sticky='e', padx=(8, 0))

        ttk.Label(frame, text='Jumlah Worker').grid(row=2, column=0, sticky='w')
        self.worker_count = tk.IntVar(value=4)
        worker_spin = ttk.Spinbox(frame, from_=2, to=32, textvariable=self.worker_count, width=6)
        worker_spin.grid(row=2, column=1, sticky='w', pady=(4, 8))

        ttk.Label(frame, text='Strategi Load Balancer').grid(row=2, column=2, sticky='w')
        self.strategy = tk.StringVar(value='equal')
        strategy_combo = ttk.Combobox(
            frame,
            textvariable=self.strategy,
            values=['equal', 'round_robin', 'weighted'],
            state='readonly',
            width=14
        )
        strategy_combo.grid(row=2, column=3, sticky='w', pady=(4, 8))

        self.run_button = ttk.Button(frame, text='Jalankan', command=self._start_run)
        self.run_button.grid(row=3, column=0, columnspan=4, sticky='we', pady=(0, 8))

        self.progress_label = ttk.Label(frame, text='Status: siap', anchor='w')
        self.progress_label.grid(row=4, column=0, columnspan=4, sticky='we', pady=(0, 8))

        self.log_text = tk.Text(frame, wrap='word', height=20, state='disabled')
        self.log_text.grid(row=5, column=0, columnspan=4, sticky='nsew')

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.log_text.yview)
        scrollbar.grid(row=5, column=4, sticky='ns')
        self.log_text['yscrollcommand'] = scrollbar.set

        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=0)
        frame.columnconfigure(3, weight=0)

    def _choose_file(self):
        path = filedialog.askopenfilename(
            title='Pilih dataset CSV',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialdir=os.path.dirname(get_default_dataset_path())
        )
        if path:
            self.dataset_path.set(path)

    def _enqueue_message(self, message: str = ''):
        self.message_queue.put(('message', message))

    def _enqueue_progress(self, current: int, total: int, prefix: str = ''):
        self.message_queue.put(('progress', prefix, current, total))

    def _schedule_queue(self):
        try:
            while True:
                item = self.message_queue.get_nowait()
                if item[0] == 'message':
                    self._append_log(item[1])
                elif item[0] == 'progress':
                    _, prefix, current, total = item
                    self._update_progress(prefix, current, total)
        except queue.Empty:
            pass
        self.after(100, self._schedule_queue)

    def _append_log(self, message: str):
        self.log_text['state'] = 'normal'
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text['state'] = 'disabled'

    def _update_progress(self, prefix: str, current: int, total: int):
        if total <= 0:
            return
        percent = min((current / total) * 100, 100.0)
        self.progress_label['text'] = f'Status: {prefix} {percent:.1f}%'
        if percent >= 100:
            self.progress_label['text'] = 'Status: selesai'

    def _start_run(self):
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return

        dataset = self.dataset_path.get().strip()
        if not dataset or not os.path.exists(dataset):
            messagebox.showerror('Error', 'Dataset tidak ditemukan')
            return

        self.run_button['state'] = 'disabled'
        self.progress_label['text'] = 'Status: memulai simulasi'
        self._append_log('Memulai simulasi...')

        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler,
            daemon=True
        )
        self.scheduler_thread.start()

    def _run_scheduler(self):
        try:
            scheduler = Scheduler(
                dataset_path=self.dataset_path.get().strip(),
                num_workers=self.worker_count.get(),
                lb_strategy=self.strategy.get(),
                output_fn=self._enqueue_message,
                progress_fn=self._enqueue_progress
            )
            scheduler.run()
            self._enqueue_message('Simulasi selesai')
        except Exception as error:
            self._enqueue_message(f'Error: {error}')
        finally:
            self.after(0, lambda: self.run_button.config(state='normal'))


def main():
    app = ParallelSchedulerGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
