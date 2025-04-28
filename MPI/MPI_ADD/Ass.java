import java.util.*;
import mpi.*;

public class ArraySumDistributed {
    public static void main(String[] args) {
        MPI.Init(args);  // Initialize the MPI environment

        int rank = MPI.COMM_WORLD.Rank();  // Get the rank (ID) of the current process
        int size = MPI.COMM_WORLD.Size();  // Get the total number of processes
        int root = 0;  // Define root process (usually process 0)

        int elementsPerProcess = 5; // Elements handled by each process
        int totalElements = elementsPerProcess * size;

        int[] fullArray = new int[totalElements];   // Complete array (only initialized by root)
        int[] subArray = new int[elementsPerProcess]; // Sub-array for each process
        int[] partialSums = new int[size]; // Array to gather intermediate sums at root

        // Step 1: Root process initializes the array
        if (rank == root) {
            System.out.println("Root initializing array:");
            for (int i = 0; i < totalElements; i++) {
                fullArray[i] = i + 1;  // Filling with numbers 1 to N
                System.out.println("Element " + i + " = " + fullArray[i]);
            }
        }

        // Step 2: Scatter the array to all processes
        MPI.COMM_WORLD.Scatter(
            fullArray, 0, elementsPerProcess, MPI.INT,
            subArray, 0, elementsPerProcess, MPI.INT,
            root
        );

        // Step 3: Each process calculates its local sum
        int localSum = 0;
        for (int i = 0; i < elementsPerProcess; i++) {
            localSum += subArray[i];
        }
        System.out.println("Process " + rank + " intermediate sum = " + localSum);

        // Step 4: Gather all local sums at root
        MPI.COMM_WORLD.Gather(
            new int[]{localSum}, 0, 1, MPI.INT,
            partialSums, 0, 1, MPI.INT,
            root
        );

        // Step 5: Root calculates the final sum
        if (rank == root) {
            int finalSum = 0;
            for (int i = 0; i < size; i++) {
                finalSum += partialSums[i];
            }
            System.out.println("Final Sum of all elements = " + finalSum);
        }

        MPI.Finalize(); // End the MPI environment
    }
}
