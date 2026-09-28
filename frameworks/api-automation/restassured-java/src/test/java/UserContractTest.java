package tests;

import core.specs.RequestSpecFactory;
import models.UserDto;

/**
 * Enterprise API Test verifying DTO builders, contract constraints, and spec factory.
 */
public class UserContractTest {

    public void testUserCreationContract() {
        UserDto newUser = UserDto.builder()
                .id(101L)
                .name("Manjunath H K")
                .email("manjunathhk833@gmail.com")
                .role("SENIOR_SDET")
                .active(true)
                .build();

        assert newUser.getId() == 101L : "User ID incorrect";
        assert newUser.getName().equals("Manjunath H K") : "User name incorrect";
        assert newUser.getRole().equals("SENIOR_SDET") : "Role incorrect";
        assert newUser.getActive() : "Active flag incorrect";

        RequestSpecFactory spec = RequestSpecFactory.defaultSpec().withBearerToken("mock_bearer_jwt");
        assert spec.getHeaders().get("Authorization").equals("Bearer mock_bearer_jwt") : "Bearer auth header missing";
    }

    public static void main(String[] args) {
        UserContractTest test = new UserContractTest();
        test.testUserCreationContract();
        System.out.println("UserContractTest assertions passed successfully!");
    }
}
