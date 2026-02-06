import subprocess
import numpy as np
from scipy.optimize import minimize
import sys
import struct
import requests

call_count = 0
cache = {}

def get_values(x, y, z, use_cache=True):
    """Get the 4 target cell values for given parameters"""
    global call_count, cache
    
    # Round to 6 decimal places (as done internally)
    x = round(x, 6)
    y = round(y, 6)
    z = round(z, 6)
    
    # Check cache
    key = (x, y, z)
    if use_cache and key in cache:
        return cache[key]
    
    call_count += 1
    
    try:
        result = subprocess.run(
            ['node', './verify.js', str(x), str(y), str(z)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd='.'
        )
        
        if result.returncode != 0:
            print(f"\n❌ Error: {result.stderr}")
            return None
        
        values = np.array([float(v) for v in result.stdout.strip().split()])
        
        if len(values) != 4:
            print(f"\n❌ Expected 4 values, got {len(values)}")
            return None
        
        # Cache the result
        cache[key] = values
        return values
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None


def objective(params, target):
    """Objective function - returns error"""
    x, y, z = params
    
    # Enforce bounds
    x = np.clip(x, 0, 100)
    y = np.clip(y, 0, 100)
    z = np.clip(z, 0, 100)
    
    current = get_values(x, y, z)
    
    if current is None:
        return 1e10
    
    error = np.linalg.norm(current - target)
    return error


def solve_reverse_engineering(target, strategy='smart'):
    """
    Solve the inverse problem with different strategies
    
    Strategies:
    - 'smart': Use domain knowledge (recommended)
    - 'differential_evolution': Global optimization
    - 'grid': Exhaustive grid search (slow but thorough)
    """
    
    target = np.array(target)
    print(f"\n🎯 Target: {target}")
    
    
    return solve_smart(target)


def solve_smart(target):
    """Smart strategy using domain knowledge"""
    
    print("\n" + "="*70)
    print("PHASE 1: Find optimal X (zoom/frequency)")
    print("="*70)
    
    # Since x controls frequency, we can estimate it from the pattern
    # Test a range of x values with y=z at midpoint
    x_range = np.linspace(0, 100, 50)
    y_mid, z_mid = 50.0, 50.0
    
    x_errors = []
    for x in x_range:
        err = objective([x, y_mid, z_mid], target)
        x_errors.append((x, err))
        if err < 1e10:  # Valid result
            print(f"  x={x:6.2f} → error={err:.6e}")
    
    # Get top 5 X candidates
    x_errors.sort(key=lambda e: e[1])
    top_x = [e[0] for e in x_errors[:5]]
    
    print(f"\n✅ Top X candidates: {[f'{x:.2f}' for x in top_x]}")
    
    print("\n" + "="*70)
    print("PHASE 2: Grid search Y-Z for each X candidate")
    print("="*70)
    
    best_params = None
    best_error = float('inf')
    
    for x_cand in top_x:
        print(f"\n--- X = {x_cand:.4f} ---")
        
        # Coarse grid on Y, Z
        y_range = np.linspace(0, 100, 20)
        z_range = np.linspace(0, 100, 20)
        
        local_best = None
        local_best_err = float('inf')
        
        for i, y in enumerate(y_range):
            for z in z_range:
                err = objective([x_cand, y, z], target)
                
                if err < local_best_err:
                    local_best_err = err
                    local_best = [x_cand, y, z]
                    
                if err < best_error:
                    best_error = err
                    best_params = [x_cand, y, z]
                    print(f"  ⭐ NEW BEST: y={y:6.2f} z={z:6.2f} → error={err:.6e}")
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"    Progress: {i+1}/{len(y_range)} y values tested")
    
    print("\n" + "="*70)
    print("PHASE 3: Fine-grained refinement")
    print("="*70)
    print(f"Starting: x={best_params[0]:.6f}, y={best_params[1]:.6f}, z={best_params[2]:.6f}")
    print(f"Error: {best_error:.8e}\n")
    
    # Local optimization
    result = minimize(
        objective,
        best_params,
        args=(target,),
        method='Nelder-Mead',
        bounds=[(0, 100), (0, 100), (0, 100)],
        options={'maxiter': 300, 'xatol': 1e-8, 'fatol': 1e-10}
    )
    
    # Round to 6 decimals
    solution = np.round(result.x, 6)
    
    # Clip to valid range
    solution = np.clip(solution, 0, 100)
    
    return solution, result.fun


def from_u64(u64_val):
    """Convert uint64 (int or string) to double"""
    if isinstance(u64_val, str):
        u64_val = int(u64_val)
    # Pack uint64 to bytes (little-endian), then unpack as double
    return struct.unpack('<d', struct.pack('<Q', u64_val))[0]

if __name__ == '__main__':
    strategy = sys.argv[5] if len(sys.argv) > 5 else 'smart'
    TARGET_URL = "http://host3.dreamhack.games:21160"
    
    print("="*70)
    print("TINYVAULT OPTIMIZED INVERSE SOLVER")
    print("="*70)
    print(f"Constraints: x, y, z ∈ [0, 100] with 6 decimal precision")
    print(f"Strategy: {strategy}")
    
    # Test setup
    print("\n🔧 Testing setup...")
    test = get_values(50.0, 50.0, 50.0)
    if test is None:
        print("❌ Setup failed!")
        sys.exit(1)
    print(f"✅ Setup OK! Test result: {test}")
    
    # Solve
    tries = 1
    solution_correct = None
    while True:
        print("="*70)
        print(f"TRYING FOR THE {tries} TIMES")
        print("="*70)
        res = requests.get(TARGET_URL + '/target')
        target = res.json()['targets']
        target = [from_u64(val) for val in target]


        solution, error = solve_reverse_engineering(target, strategy)
        
        # Display results
        print("\n" + "="*70)
        print("🎉 SOLUTION FOUND")
        print("="*70)
        print(f"x = {solution[0]:.6f}")
        print(f"y = {solution[1]:.6f}")
        print(f"z = {solution[2]:.6f}")
        print(f"\nFinal error: {error:.10e}")
        print(f"Function calls: {call_count}")
        print(f"Cached results: {len(cache)}")
        
        # Verification
        print("\n" + "="*70)
        print("✓ VERIFICATION")
        print("="*70)
        result = get_values(solution[0], solution[1], solution[2])
        tries += 1
        
        if result is not None:
            diff = result - np.array(target)
            
            print(f"Target: {target}")
            print(f"Result: {result.tolist()}")
            print(f"Diff:   {diff.tolist()}")
            print(f"Max error: {np.max(np.abs(diff)):.10e}")
            
            if np.max(np.abs(diff)) < 1e-6:
                print("\n✅ SUCCESS! Solution matches target!")
                solution_correct = solution
                break
            elif np.max(np.abs(diff)) < 1e-3:
                print("\n⚠️  Close, but may need refinement")
            else:
                print("\n❌ Not close enough - try different strategy")

    res = requests.post(TARGET_URL + '/verify', json={
        "x": solution_correct[0],
        "y": solution_correct[1],
        "z": solution_correct[2]
    })

    print(res.json())