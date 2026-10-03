package models;

import java.util.Objects;

/**
 * Data Transfer Object representing a User payload with Builder pattern.
 */
public class UserDto {
    private Long id;
    private String name;
    private String email;
    private String role;
    private Boolean active;

    public UserDto() {}

    public UserDto(Long id, String name, String email, String role, Boolean active) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.role = role;
        this.active = active;
    }

    public static Builder builder() {
        return new Builder();
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    public Boolean getActive() { return active; }

    public void setId(Long id) { this.id = id; }
    public void setName(String name) { this.name = name; }
    public void setEmail(String email) { this.email = email; }
    public void setRole(String role) { this.role = role; }
    public void setActive(Boolean active) { this.active = active; }

    public static class Builder {
        private Long id;
        private String name;
        private String email;
        private String role = "ENGINEER";
        private Boolean active = true;

        public Builder id(Long id) { this.id = id; return this; }
        public Builder name(String name) { this.name = name; return this; }
        public Builder email(String email) { this.email = email; return this; }
        public Builder role(String role) { this.role = role; return this; }
        public Builder active(Boolean active) { this.active = active; return this; }

        public UserDto build() {
            return new UserDto(id, name, email, role, active);
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UserDto userDto = (UserDto) o;
        return Objects.equals(id, userDto.id) && Objects.equals(name, userDto.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name);
    }
}
