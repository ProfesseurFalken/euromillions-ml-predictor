#!/usr/bin/env python3
"""
Quick analysis of current prediction patterns and performance
"""
import numpy as np
from repository import get_repository
from train_models import get_model_info

def analyze_current_state():
    """Analyze current data and model performance"""
    
    print("=" * 60)
    print("CURRENT PREDICTION SYSTEM ANALYSIS")
    print("=" * 60)
    
    # Database analysis
    repo = get_repository()
    df = repo.all_draws_df()
    
    print(f"\n📊 DATA STATISTICS:")
    print(f"   Total draws: {len(df)}")
    print(f"   Date range: {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    # Number frequency analysis
    all_nums = []
    for i in range(1, 6):
        all_nums.extend(df[f'n{i}'].values)
    
    unique, counts = np.unique(all_nums, return_counts=True)
    freq_dict = dict(zip(unique, counts))
    sorted_freq = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n🎱 NUMBER FREQUENCY (Top 10 most drawn):")
    for num, count in sorted_freq[:10]:
        percentage = (count / len(df)) * 100
        print(f"   {int(num):2d}: {count:4d} times ({percentage:.1f}%)")
    
    print(f"\n🎱 NUMBER FREQUENCY (Top 10 least drawn):")
    for num, count in sorted_freq[-10:]:
        percentage = (count / len(df)) * 100
        print(f"   {int(num):2d}: {count:4d} times ({percentage:.1f}%)")
    
    # Star frequency
    all_stars = []
    all_stars.extend(df['s1'].values)
    all_stars.extend(df['s2'].values)
    
    unique_s, counts_s = np.unique(all_stars, return_counts=True)
    freq_dict_s = dict(zip(unique_s, counts_s))
    sorted_freq_s = sorted(freq_dict_s.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n⭐ STAR FREQUENCY:")
    for num, count in sorted_freq_s:
        percentage = (count / len(df)) * 100
        print(f"   {int(num):2d}: {count:4d} times ({percentage:.1f}%)")
    
    # Model performance
    print(f"\n🤖 CURRENT MODEL PERFORMANCE:")
    try:
        info = get_model_info()
        if info.get('models_available'):
            print(f"   Main numbers log-loss: {info['performance']['main_logloss']:.4f}")
            print(f"   Stars log-loss: {info['performance']['star_logloss']:.4f}")
            print(f"   Training data: {info['data_range']['n_draws']} draws")
            print(f"   Features used: {', '.join(info['features'])}")
        else:
            print("   No trained models found")
    except Exception as e:
        print(f"   Error loading model info: {e}")
    
    # Pattern analysis
    print(f"\n🔍 RECENT PATTERNS (Last 20 draws):")
    recent = df.tail(20)
    
    # Even/odd ratio in recent draws
    even_count = 0
    odd_count = 0
    for _, draw in recent.iterrows():
        for i in range(1, 6):
            num = draw[f'n{i}']
            if num % 2 == 0:
                even_count += 1
            else:
                odd_count += 1
    
    print(f"   Even/Odd ratio: {even_count}/{odd_count} ({even_count/(even_count+odd_count)*100:.1f}% even)")
    
    # High/low ratio (1-25 vs 26-50)
    low_count = 0
    high_count = 0
    for _, draw in recent.iterrows():
        for i in range(1, 6):
            num = draw[f'n{i}']
            if num <= 25:
                low_count += 1
            else:
                high_count += 1
    
    print(f"   Low/High ratio: {low_count}/{high_count} ({low_count/(low_count+high_count)*100:.1f}% low [1-25])")
    
    # Consecutive numbers
    consecutive_count = 0
    for _, draw in recent.iterrows():
        nums = sorted([draw[f'n{i}'] for i in range(1, 6)])
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                consecutive_count += 1
    
    print(f"   Consecutive pairs: {consecutive_count} in last 20 draws")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_current_state()
