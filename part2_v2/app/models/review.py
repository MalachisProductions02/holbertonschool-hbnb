from .base_model import BaseModel

class Review(BaseModel):
    """Review template with rating validation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.text = kwargs.get('text', '')
        self.rating = kwargs.get('rating', 0)
        self.place_id = kwargs.get('place_id', '')
        self.user_id = kwargs.get('user_id', '')
        
        self.validate()

    def validate(self):
        """Validate the rating and text"""
        if not self.text:
            raise ValueError("Review text is required")
            
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
