"""
Quick test to verify warning fix
"""
import warnings
from train_improved import train_improved

# Capture warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    print("Testing improved training with warning fix...")
    print("Running single fold test...")
    print()
    
    try:
        result = train_improved(min_rows=200)
        
        # Check for UserWarnings about probabilities
        prob_warnings = [warning for warning in w 
                        if "sum to one" in str(warning.message)]
        
        if prob_warnings:
            print(f"[FAIL] Still have {len(prob_warnings)} probability warnings")
            for warning in prob_warnings[:3]:
                print(f"   {warning.message}")
        else:
            print("[PASS] No probability warnings!")
        
        print()
        print("Performance:")
        print(f"   Main: {result['performance']['main_logloss']:.4f}")
        print(f"   Star: {result['performance']['star_logloss']:.4f}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
