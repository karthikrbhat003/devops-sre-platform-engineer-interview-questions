package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
)

// getKubeConfig returns cluster rest config (in-cluster or local kubeconfig fallback)
func getKubeConfig() (*rest.Config, error) {
	config, err := rest.InClusterConfig()
	if err == nil {
		return config, nil
	}
	home, _ := os.UserHomeDir()
	kubeconfigPath := filepath.Join(home, ".kube", "config")
	return clientcmd.BuildConfigFromFlags("", kubeconfigPath)
}

func main() {
	config, err := getKubeConfig()
	if err != nil {
		log.Fatalf("Error building kubeconfig: %v", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatalf("Error building kubernetes clientset: %v", err)
	}

	// Create SharedInformerFactory with 10-minute resync interval
	factory := informers.NewSharedInformerFactory(clientset, 10*time.Minute)
	podInformer := factory.Core().V1().Pods().Informer()

	// Register event handlers
	podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			pod := obj.(*corev1.Pod)
			fmt.Printf("🟢 [POD CREATED] Namespace: %s | Name: %s | Node: %s\n",
				pod.Namespace, pod.Name, pod.Spec.NodeName)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			newPod := newObj.(*corev1.Pod)
			// Inspect container status for CrashLoopBackOff or OOMKilled
			for _, cs := range newPod.Status.ContainerStatuses {
				if cs.State.Waiting != nil && cs.State.Waiting.Reason == "CrashLoopBackOff" {
					fmt.Printf("🚨 [CRASHLOOP DETECTED] Namespace: %s | Pod: %s | Container: %s | Restarts: %d\n",
						newPod.Namespace, newPod.Name, cs.Name, cs.RestartCount)
				}
				if cs.LastTerminationState.Terminated != nil && cs.LastTerminationState.Terminated.Reason == "OOMKilled" {
					fmt.Printf("💥 [OOMKILLED DETECTED] Namespace: %s | Pod: %s | ExitCode: %d\n",
						newPod.Namespace, newPod.Name, cs.LastTerminationState.Terminated.ExitCode)
				}
			}
		},
		DeleteFunc: func(obj interface{}) {
			pod := obj.(*corev1.Pod)
			fmt.Printf("🔴 [POD DELETED] Namespace: %s | Name: %s\n", pod.Namespace, pod.Name)
		},
	})

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	fmt.Println("🚀 Starting Kubernetes Pod Informer Watcher...")
	factory.Start(ctx.Done())

	// Wait for cache to sync before processing
	if !cache.WaitForCacheSync(ctx.Done(), podInformer.HasSynced) {
		log.Fatalf("Timed out waiting for informer caches to sync")
	}

	fmt.Println("✅ Informer cache synced. Monitoring active.")
	<-ctx.Done()
}
