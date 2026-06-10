from .main import main
import time

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    execution_time = execution_time / 60
    print(f"Execution time: {execution_time:.4f} min")
