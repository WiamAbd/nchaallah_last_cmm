from .main import main
import time

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = execution_time / 60
    print(f"Execution time: {execution_time:.4f} min")
