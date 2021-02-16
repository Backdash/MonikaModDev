init 20 python in mas_stories:
    def dev_unlock_all_stories():
        """
        Dev function, unlocks all stories
        """
        for story in story_database.itervalues():
            story.unlocked=True
