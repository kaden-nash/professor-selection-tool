from tqdm import tqdm 
import threading
from typing import Optional, Any

class Monitor:
    def __init__(self):
        """
        Manages tqdm progress bars for professors and reviews.
        Uses locks if multiple threads might update progress simultaneously.
        """
        self.prof_pbar: Optional[Any] = None
        self.review_pbar: Optional[Any] = None
        self.lock = threading.Lock()
        
    def init_professors(self, total: int):
        with self.lock:
            self.prof_pbar = tqdm(total=total, desc="Professors fetched", position=0)
        
    def update_professors(self, n: int = 1):
        with self.lock:
            if self.prof_pbar is not None:
                self.prof_pbar.update(n)  
                
    def init_reviews(self, total: int):
        with self.lock:
            self.review_pbar = tqdm(total=total, desc="Professor reviews fetched", position=1)
            
    def update_reviews(self, n: int = 1):
        with self.lock:
            if self.review_pbar is not None:
                self.review_pbar.update(n)  
                
    def close(self):
        with self.lock:
            try:
                if self.prof_pbar is not None:
                    self.prof_pbar.close()  
            except Exception:
                pass
            try:
                if self.review_pbar is not None:
                    self.review_pbar.close()  
            except Exception:
                pass
