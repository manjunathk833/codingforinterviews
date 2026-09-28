import java.util.*;

public class Solution {

    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        Arrays.sort(nums);

        for (int i = 0; i < nums.length - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;

            int left = i + 1, right = nums.length - 1;
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (sum == 0) {
                    res.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    left++;
                    right--;
                    while (left < right && nums[left] == nums[left - 1]) left++;
                    while (left < right && nums[right] == nums[right + 1]) right--;
                } else if (sum < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return res;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        List<List<Integer>> res1 = sol.threeSum(new int[] { -1, 0, 1, 2, -1, -4 });
        assert res1.size() == 2 : "Test 1 Failed: Expected 2 triplets, got " + res1.size();

        List<List<Integer>> res2 = sol.threeSum(new int[] { 0, 1, 1 });
        assert res2.isEmpty() : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
