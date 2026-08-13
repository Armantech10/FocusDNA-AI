import numpy as np
import pandas as pd
from typing import Tuple

def generate_behavioral_dataset(num_samples: int = 1200, random_seed: int = 42) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Generates synthetic behavioral feature matrix X and target label y for training.
    
    Features:
    - switch_frequency_5m: Context switches in last 5 minutes (0 to 25)
    - social_media_ratio: Proportion of time on social media (0.0 to 1.0)
    - entertainment_ratio: Proportion of time on entertainment (0.0 to 1.0)
    - idle_ratio: Proportion of idle time (0.0 to 1.0)
    - session_elapsed_minutes: Minutes elapsed in session (0 to 120)
    - time_of_day_hour: Hour of day (0 to 23)
    
    Target:
    - attention_loss_risk: 1 if high risk of attention loss in next 10m, 0 otherwise.
    """
    np.random.seed(random_seed)

    switches = np.random.poisson(lam=4, size=num_samples)
    social_ratio = np.random.beta(a=0.5, b=2.0, size=num_samples)
    entertainment_ratio = np.random.beta(a=0.3, b=2.5, size=num_samples)
    idle_ratio = np.random.beta(a=0.3, b=3.0, size=num_samples)
    session_elapsed = np.random.uniform(0, 120, size=num_samples)
    hour = np.random.randint(0, 24, size=num_samples)

    # Calculate ground truth probability based on behavioral mechanics
    log_odds = (
        -2.5 
        + 0.28 * switches 
        + 3.2 * social_ratio 
        + 2.8 * entertainment_ratio 
        + 2.0 * idle_ratio 
        + 0.02 * session_elapsed
        + 0.05 * np.where((hour >= 14) & (hour <= 16), 1.5, 0) # Afternoon fatigue slump
    )
    
    prob = 1.0 / (1.0 + np.exp(-log_odds))
    y = (prob > 0.45).astype(int)

    X = pd.DataFrame({
        "switch_frequency_5m": switches,
        "social_media_ratio": np.round(social_ratio, 3),
        "entertainment_ratio": np.round(entertainment_ratio, 3),
        "idle_ratio": np.round(idle_ratio, 3),
        "session_elapsed_minutes": np.round(session_elapsed, 1),
        "time_of_day_hour": hour
    })

    y_series = pd.Series(y, name="attention_loss_risk")
    return X, y_series

if __name__ == "__main__":
    X, y = generate_behavioral_dataset()
    print(f"Generated dataset with {X.shape[0]} samples across {X.shape[1]} features.")
    print("Class distribution:\n", y.value_counts(normalize=True))
