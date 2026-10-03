import java.util.*;

/**
 * SDET Challenge: Fluent Test Data Factory with Deep Clone Mutator
 */
public class Solution {

    public static class TestUser {
        private String id;
        private String name;
        private String email;
        private List<String> permissions;

        public TestUser(String id, String name, String email, List<String> permissions) {
            this.id = id;
            this.name = name;
            this.email = email;
            this.permissions = new ArrayList<>(permissions);
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public String getEmail() { return email; }
        public List<String> getPermissions() { return Collections.unmodifiableList(permissions); }
    }

    public static class TestUserFactory {
        private String id = "USR-" + System.currentTimeMillis();
        private String name = "Default Candidate";
        private String email = "candidate@maang.com";
        private List<String> permissions = new ArrayList<>(Arrays.asList("READ", "WRITE"));

        public static TestUserFactory aDefaultUser() {
            return new TestUserFactory();
        }

        public TestUserFactory withName(String name) {
            this.name = name;
            return this;
        }

        public TestUserFactory withEmail(String email) {
            this.email = email;
            return this;
        }

        public TestUserFactory withPermissions(String... perms) {
            this.permissions = new ArrayList<>(Arrays.asList(perms));
            return this;
        }

        public TestUser build() {
            return new TestUser(this.id, this.name, this.email, this.permissions);
        }
    }

    public static void main(String[] args) {
        // Test 1: Generate standard baseline user
        TestUser user1 = TestUserFactory.aDefaultUser().build();
        assert user1.getName().equals("Default Candidate") : "Test 1 Failed";
        assert user1.getPermissions().contains("READ") : "Test 1 Failed";

        // Test 2: Fluent override does not mutate prototype or previous instances
        TestUser user2 = TestUserFactory.aDefaultUser()
                .withName("Admin Manjunath")
                .withPermissions("ADMIN", "READ", "WRITE", "DELETE")
                .build();

        assert user2.getName().equals("Admin Manjunath") : "Test 2 Failed";
        assert user2.getPermissions().size() == 4 : "Test 2 Failed";
        assert user1.getPermissions().size() == 2 : "Test 2 Failed: user1 was mutated!";

        System.out.println("All 2 Java Test Data Factory test cases passed!");
    }
}
