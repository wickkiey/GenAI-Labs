# SQL Agent

This scaffold covers NL-to-SQL work, verification, and safe execution patterns.

What I built: a project shell for a read-only SQL agent with clear validation steps before execution.
What surprised me: safe execution matters more than model quality when the task touches a real database.
What broke: unguarded SQL execution can accidentally run writes even when the prompt seems harmless.
