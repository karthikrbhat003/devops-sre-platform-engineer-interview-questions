package main

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"
)

// Task represents a unit of work to be processed
type Task struct {
	ID       int
	Payload  string
	Duration time.Duration
}

// Result represents the outcome of a Task execution
type Result struct {
	TaskID int
	Output string
	Err    error
}

// WorkerPool manages concurrent worker goroutines with bounded buffer and graceful cancellation
type WorkerPool struct {
	numWorkers int
	tasksChan  chan Task
	resultsChan chan Result
	wg         sync.WaitGroup
}

// NewWorkerPool initializes a WorkerPool with fixed concurrency
func NewWorkerPool(numWorkers, bufferSize int) *WorkerPool {
	return &WorkerPool{
		numWorkers:  numWorkers,
		tasksChan:   make(chan Task, bufferSize),
		resultsChan: make(chan Result, bufferSize),
	}
}

// Start launches worker goroutines
func (wp *WorkerPool) Start(ctx context.Context) {
	for i := 1; i <= wp.numWorkers; i++ {
		wp.wg.Add(1)
		go wp.worker(ctx, i)
	}
}

func (wp *WorkerPool) worker(ctx context.Context, workerID int) {
	defer wp.wg.Done()
	for {
		select {
		case <-ctx.Done():
			fmt.Printf("[Worker %d] Received cancellation signal. Exiting...\n", workerID)
			return
		case task, ok := <-wp.tasksChan:
			if !ok {
				// Channel closed, drain complete
				return
			}
			// Process task
			res := wp.processTask(ctx, workerID, task)
			select {
			case wp.resultsChan <- res:
			case <-ctx.Done():
				return
			}
		}
	}
}

func (wp *WorkerPool) processTask(ctx context.Context, workerID int, task Task) Result {
	select {
	case <-time.After(task.Duration):
		if task.ID == 13 {
			return Result{TaskID: task.ID, Err: errors.New("simulated error on task 13")}
		}
		return Result{
			TaskID: task.ID,
			Output: fmt.Sprintf("Processed by worker %d in %v", workerID, task.Duration),
		}
	case <-ctx.Done():
		return Result{TaskID: task.ID, Err: ctx.Err()}
	}
}

// Submit enqueues a new task
func (wp *WorkerPool) Submit(task Task) {
	wp.tasksChan <- task
}

// Close closes the tasks channel and waits for workers to finish
func (wp *WorkerPool) Stop() {
	close(wp.tasksChan)
	wp.wg.Wait()
	close(wp.resultsChan)
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	pool := NewWorkerPool(4, 20)
	pool.Start(ctx)

	// Producer: Submit 15 tasks
	go func() {
		for i := 1; i <= 15; i++ {
			pool.Submit(Task{
				ID:       i,
				Payload:  fmt.Sprintf("Job-%d", i),
				Duration: time.Duration(100*(i%5+1)) * time.Millisecond,
			})
		}
		pool.Stop()
	}()

	// Consumer: Process results
	for res := range pool.resultsChan {
		if res.Err != nil {
			fmt.Printf("❌ Task %d failed: %v\n", res.TaskID, res.Err)
		} else {
			fmt.Printf("✅ Task %d success: %s\n", res.TaskID, res.Output)
		}
	}
	fmt.Println("All tasks processed successfully.")
}
